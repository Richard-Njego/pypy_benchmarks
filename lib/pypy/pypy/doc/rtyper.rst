The RPython Typer
=================

.. contents::


The RPython Typer lives in the directory `rpython/rtyper/`_.


Overview
--------

The RPython Typer is the bridge between the Annotator_ and the low-level code
generators.  The annotations of the Annotator_ are high-level, in the sense
that they describe RPython types like lists or instances of user-defined
classes.  In general, though, to emit code we need to represent these
high-level annotations in the low-level model of the target language; for C,
this means structures and pointers and arrays.  The Typer both determines the
appropriate low-level type for each annotation, and tries to replace *all*
operations in the control flow graphs with one or a few low-level operations.
Just like low-level types, there is only a fairly restricted set of low-level
operations, along the lines of reading or writing from or to a field of a
structure.

In theory, this step is optional; some code generators might be able to read
the high-level types directly.  However, we expect that case to be the
exception.  "Compiling" high-level types into low-level ones is rather more
messy than one would expect.  This was the motivation for making this step
explicit and isolated in a single place.  After Typing, the graphs can only
contain very few operations, which makes the job of the code generators much
simpler.


Example: Integer operations
---------------------------

Integer operations are the easiest.  Assume a graph containing the following
operation::

    v3 = add(v1, v2)

annotated::

    v1 -> SomeInteger()
    v2 -> SomeInteger()
    v3 -> SomeInteger()

then obviously we want to type it and replace it with::

    v3 = int_add(v1, v2)

where -- in C notation -- all three variables v1, v2 and v3 are typed ``int``.
This is done by attaching an attribute ``concretetype`` to v1, v2 and v3
(which might be instances of Variable or possibly Constant).  In our model,
this ``concretetype`` is ``rpython.rtyper.lltypesystem.lltype.Signed``.  Of
course, the purpose of replacing the operation called ``add`` with
``int_add`` is that code generators no longer have to worry about what kind
of addition (or concatenation maybe?) it means.


The process in more details
---------------------------

The RPython Typer has a structure similar to that of the Annotator_: both
consider each block of the flow graphs in turn, and perform some analysis on
each operation.  In both cases the analysis of an operation depends on the
annotations of its input arguments.  This is reflected in the usage of the same
``__extend__`` syntax in the source files (compare e.g.
`rpython/annotator/binaryop.py`_ and `rpython/rtyper/rint.py`_).

The analogy stops here, though: while it runs, the Annotator is in the middle
of computing the annotations, so it might need to reflow and generalize until
a fixpoint is reached.  The Typer, by contrast, works on the final annotations
that the Annotator computed, without changing them, assuming that they are
globally consistent.  There is no need to reflow: the Typer considers each
block only once.  And unlike the Annotator, the Typer completely modifies the
flow graph, by replacing each operation with some low-level operations.

In addition to replacing operations, the RTyper creates a ``concretetype``
attribute on all Variables and Constants in the flow graphs, which tells code
generators which type to use for each of them.  This attribute is a
`low-level type`_, as described below.


Representations
---------------

Representations -- the Repr classes -- are the most important internal classes
used by the RTyper.  (They are internal in the sense that they are an
"implementation detail" and their instances just go away after the RTyper is
finished; the code generators should only use the ``concretetype`` attributes,
which are not Repr instances but `low-level types`_.)

A representation contains all the logic about mapping a specific SomeXxx()
annotation to a specific low-level type.  For the time being, the RTyper
assumes that each SomeXxx() instance needs only one "canonical" representation.
For example, all variables annotated with SomeInteger() will correspond to the
``Signed`` low-level type via the ``IntegerRepr`` representation.  More subtly,
variables annotated SomeList() can correspond either to a structure holding an
array of items of the correct type, or -- if the list in question is just a
range() with a constant step -- a structure with just start and stop fields.

This example shows that two representations may need very different low-level
implementations for the same high-level operations.  This is the reason for
turning representations into explicit objects.

The base Repr class is defined in `rpython/rtyper/rmodel.py`_.  Most of the
``rpython/r*.py`` files define one or a few subclasses of Repr.  The method
getrepr() of the RTyper will build and cache a single Repr instance per
SomeXxx() instance; moreover, two SomeXxx() instances that are equal get the
same Repr instance.

The key attribute of a Repr instance is called ``lowleveltype``, which is what
gets copied into the attribute ``concretetype`` of the Variables that have been
given this representation.  The RTyper also computes a ``concretetype`` for
Constants, to match the way they are used in the low-level operations (for
example, ``int_add(x, 1)`` requires a ``Constant(1)`` with
``concretetype=Signed``, but an untyped ``add(x, 1)`` works with a
``Constant(1)`` that must actually be a PyObject at run-time).

In addition to ``lowleveltype``, each Repr subclass provides a set of methods
called ``rtype_op_xxx()`` which define how each high-level operation ``op_xxx``
is turned into low-level operations.


.. _`low-level type`:

Low-Level Types
---------------

The RPython Typer uses a standard low-level model which we believe can
correspond rather directly to various target languages such as C.
This model is implemented in the first part of
`rpython/rtyper/lltypesystem/lltype.py`_.

The second part of `rpython/rtyper/lltypesystem/lltype.py`_ is a runnable
implementation of these types, for testing purposes.  It allows us to write
and test plain Python code using a malloc() function to obtain and manipulate
structures and arrays.  This is useful for example to implement and test
RPython types like 'list' with its operations and methods.

The basic assumption is that Variables (i.e. local variables and function
arguments and return value) all contain "simple" values: basically, just
integers or pointers.  All the "container" data structures (struct and array)
are allocated in the heap, and they are always manipulated via pointers.
(There is no equivalent to the C notion of local variable of a ``struct`` type.)

Here is a quick tour:

    >>> from rpython.rtyper.lltypesystem.lltype import *

Here are a few primitive low-level types, and the typeOf() function to figure
them out:

    >>> Signed
    <Signed>
    >>> typeOf(5)
    <Signed>
    >>> typeOf(r_uint(12))
    <Unsigned>
    >>> typeOf('x')
    <Char>

Let's say that we want to build a type "point", which is a structure with two
integer fields "x" and "y":

    >>> POINT = GcStruct('point', ('x', Signed), ('y', Signed))
    >>> POINT
    <GcStruct point { x: Signed, y: Signed }>

The structure is a ``GcStruct``, which means a structure that can be allocated
in the heap and eventually freed by some garbage collector.  (For platforms
where we use reference counting, think about ``GcStruct`` as a struct with an
additional reference counter field.)

Giving a name ('point') to the GcStruct is only for clarity: it is used in the
representation.

    >>> p = malloc(POINT)
    >>> p
    <* struct point { x=0, y=0 }>
    >>> p.x = 5
    >>> p.x
    5
    >>> p
    <* struct point { x=5, y=0 }>

``malloc()`` allocates a structure from the heap, initializes it to 0
(currently), and returns a pointer to it.  The point of all this is to work with
a very limited, easily controllable set of types, and define implementations of
types like list in this elementary world.  The ``malloc()`` function is a kind
of placeholder, which must eventually be provided by the code generator for the
target platform; but as we have just seen its Python implementation in
`rpython/rtyper/lltypesystem/lltype.py`_ works too, which is primarily useful for
testing, interactive exploring, etc.

The argument to ``malloc()`` is the structure type directly, but it returns a
pointer to the structure, as ``typeOf()`` tells you:

    >>> typeOf(p)
    <* GcStruct point { x: Signed, y: Signed }>

For the purpose of creating structures with pointers to other structures, we can
declare pointer types explicitly:

    >>> typeOf(p) == Ptr(POINT)
    True
    >>> BIZARRE = GcStruct('bizarre', ('p1', Ptr(POINT)), ('p2', Ptr(POINT)))
    >>> b = malloc(BIZARRE)
    >>> b.p1
    <* None>
    >>> b.p1 = b.p2 = p
    >>> b.p1.y = 42
    >>> b.p2.y
    42

The world of low-level types is more complicated than integers and GcStructs,
though.  The next pages are a reference guide.


Primitive Types
+++++++++++++++

Signed
    a signed integer in one machine word (a ``long``, in C)

Unsigned
    a non-signed integer in one machine word (``unsigned long``)

Float
    a 64-bit float (``double``)

Char
    a single character (``char``)

Bool
    a boolean value

Void
    a constant.  Meant for variables, function arguments, structure fields, etc.
    which should disappear from the generated code.


Structure Types
+++++++++++++++

Structure types are built as instances of 
``rpython.rtyper.lltypesystem.lltype.Struct``::

    MyStructType = Struct('somename',  ('field1', Type1), ('field2', Type2)...)
    MyStructType = GcStruct('somename',  ('field1', Type1), ('field2', Type2)...)

This declares a structure (or a Pascal ``record``) containing the specified
named fields with the given types.  The field names cannot start with an
underscore.  As noted above, you cannot directly manipulate structure objects,
but only pointer to structures living in the heap.

By contrast, the fields themselves can be of primitive, pointer or container
type.  When a structure contains another structure as a field we say that the
latter is "inlined" in the former: the bigger structure contains the smaller one
as part of its memory layout.

A structure can also contain an inlined array (see below), but only as its last
field: in this case it is a "variable-sized" structure, whose memory layout
starts with the non-variable fields and ends with a variable number of array
items.  This number is determined when a structure is allocated in the heap.
Variable-sized structures cannot be inlined in other structures.

GcStructs have a platform-specific GC header (e.g. a reference counter); only
these can be dynamically malloc()ed.  The non-GC version of Struct does not have
any header, and is suitable for being embedded ("inlined") inside other
structures.  As an exception, a GcStruct can be embedded as the first field of a
GcStruct: the parent structure uses the same GC header as the substructure.


Array Types
+++++++++++

An array type is built as an instance of 
``rpython.rtyper.lltypesystem.lltype.Array``::

    MyIntArray = Array(Signed)
    MyOtherArray = Array(MyItemType)
    MyOtherArray = GcArray(MyItemType)

Or, for arrays whose items are structures, as a shortcut::

    MyArrayType = Array(('field1', Type1), ('field2', Type2)...)

You can build arrays whose items are either primitive or pointer types, or
(non-GC non-varsize) structures.

GcArrays can be malloc()ed.  The length must be specified when malloc() is
called, and arrays cannot be resized; this length is stored explicitly in a
header.

The non-GC version of Array can be used as the last field of a structure, to
make a variable-sized structure.  The whole structure can then be malloc()ed,
and the length of the array is specified at this time.


Pointer Types
+++++++++++++

As in C, pointers provide the indirection needed to make a reference modifiable
or sharable.  Pointers can only point to a structure, an array, a function
(see below) or a PyObject (see below).  Pointers to primitive types, if needed,
must be done by pointing to a structure with a single field of the required
type.  Pointer types are declared by::

   Ptr(TYPE)

At run-time, pointers to GC structures (GcStruct, GcArray and PyObject) hold a
reference to what they are pointing to.  Pointers to non-GC structures that can
go away when their container is deallocated (Struct, Array) must be handled
with care: the bigger structure of which they are part of could be freed while
the Ptr to the substructure is still in use.  In general, it is a good idea to
avoid passing around pointers to inlined substructures of malloc()ed structures.
(The testing implementation of `rpython/rtyper/lltypesystem/lltype.py`_ checks to some
extent that you are not trying to use a pointer to a structure after its
container has been freed, using weak references.  But pointers to non-GC
structures are not officially meant to be weak references: using them after what
they point to has been freed just crashes.)

The malloc() operation allocates and returns a Ptr to a new GC structure or
array.  In a refcounting implementation, malloc() would allocate enough space
for a reference counter before the actual structure, and initialize it to 1.
Note that the testing implementation also allows malloc() to allocate a non-GC
structure or array with a keyword argument ``immortal=True``.  Its purpose is to
declare and initialize prebuilt data structures which the code generators will
turn into static immortal non-GC'ed data.


Function Types
++++++++++++++

The declaration::

    MyFuncType = FuncType([Type1, Type2, ...], ResultType)

declares a function type taking arguments of the given types and returning a
result of the given type.  All these types must be primitives or pointers.  The
function type itself is considered to be a "container" type: if you wish, a
function contains the bytes that make up its executable code.  As with
structures and arrays, they can only be manipulated through pointers.

The testing implementation allows you to "create" functions by calling
``functionptr(TYPE, name, **attrs)``.  The extra attributes describe the
function in a way that isn't fully specified now, but the following attributes
*might* be present:

    :_callable:  a Python callable, typically a function object.
    :graph:      the flow graph of the function.


The PyObject Type
+++++++++++++++++

This is a special type, for compatibility with CPython: it stands for a
structure compatible with PyObject.  This is also a "container" type (thinking
about C, this is ``PyObject``, not ``PyObject*``), so it is usually manipulated
via a Ptr.  A typed graph can still contain generic space operations (add,
getitem, etc.) provided they are applied on objects whose low-level type is
``Ptr(PyObject)``.  In fact, code generators that support this should consider
that the default type of a variable, if none is specified, is ``Ptr(PyObject)``.
In this way, they can generate the correct code for fully-untyped flow graphs.

The testing implementation allows you to "create" PyObjects by calling
``pyobjectptr(obj)``.


Opaque Types
++++++++++++

Opaque types represent data implemented in a back-end specific way.  This
data cannot be inspected or manipulated.

There is a predefined opaque type ``RuntimeTypeInfo``; at run-time, a
value of type ``RuntimeTypeInfo`` represents a low-level type.  In
practice it is probably enough to be able to represent GcStruct and
GcArray types.  This is useful if we have a pointer of type ``Ptr(S)``
which can at run-time point either to a malloc'ed ``S`` alone, or to the
``S`` first field of a larger malloc'ed structure.  The information about
the exact larger type that it points to can be computed or passed around
as a ``Ptr(RuntimeTypeInfo)``.  Pointer equality on
``Ptr(RuntimeTypeInfo)`` can be used to check the type at run-time.

At the moment, for memory management purposes, some back-ends actually
require such information to be available at run-time in the following
situation: when a GcStruct has another GcStruct as its first field.  A
reference-counting back-end needs to be able to know when a pointer to the
smaller structure actually points to the larger one, so that it can also
decref the extra fields.  Depending on the situation, it is possible to
reconstruct this information without having to store a flag in each and
every instance of the smaller GcStruct.  For example, the instances of a
class hierarchy can be implemented by nested GcStructs, with instances of
subclasses extending instances of parent classes by embedding the parent
part of the instance as the first field.  In this case, there is probably
already a way to know the run-time class of the instance (e.g. a vtable
pointer), but the back-end cannot guess this.  This is the reason for
which ``RuntimeTypeInfo`` was originally introduced: just after the
GcStruct is created, the function attachRuntimeTypeInfo() should be called
to attach to the GcStruct a low-level function of signature
``Ptr(GcStruct) -> Ptr(RuntimeTypeInfo)``.  This function will be compiled
by the back-end and automatically called at run-time.  In the above
example, it would follow the vtable pointer and fetch the opaque
``Ptr(RuntimeTypeInfo)`` from the vtable itself.  (The reference-counting
GenC back-end uses a pointer to the deallocation function as the opaque
``RuntimeTypeInfo``.)


Implementing RPython types
--------------------------

As hinted above, the RPython types (e.g. 'list') are implemented in some
"restricted-restricted Python" format by manipulating only low-level types, as
provided by the testing implementation of malloc() and friends.  What occurs
then is that the same (tested!) very-low-level Python code -- which looks really
just like C -- is then transformed into a flow graph and integrated with the
rest of the user program.  In other words, we replace an operation like ``add``
between two variables annotated as SomeList, with a ``direct_call`` operation
invoking this very-low-level list concatenation.

This list concatenation flow graph is then annotated as usual, with one
difference: the annotator has to be taught about malloc() and the way the
pointer thus obtained can be manipulated.  This generates a flow graph which is
hopefully completely annotated with SomePtr() annotation.  Introduced just for
this case, SomePtr maps directly to a low-level pointer type.  This is the only
change needed to the Annotator to allow it to perform type inference of our
very-low-level snippets of code.

See for example `rpython/rtyper/rlist.py`_.


.. _`oo type`:

Object Oriented Types
---------------------

The standard `low-level type` model described above is fine for
targeting low level backends such as C, but it is not good
enough for targeting higher level backends such as .NET CLI or Java
JVM, so a new object oriented model has been introduced. This model is
implemented in the first part of `rpython/rtyper/ootypesystem/ootype.py`_.

As for the low-level typesystem, the second part of
`rpython/rtyper/ootypesystem/ootype.py`_ is a runnable implementation of
these types, for testing purposes.


The target platform
+++++++++++++++++++

There are plenty of object oriented languages and platforms around,
each one with its own native features: they could be statically or
dynamically typed, they could support or not things like multiple
inheritance, classes and functions as first class order objects,
generics, and so on.

The goal of *ootypesystem* is to define a trade-off between all
the potential backends that let them to use the native facilities when
available while not preventing other backends to work when they
aren't.


Types and classes
+++++++++++++++++

Most of the primitive types defined in *ootypesystem* are the very
same of those found in *lltypesystem*: ``Bool``, ``Signed``,
``Unsigned``, ``Float``, ``Char``, ``UniChar`` and ``Void``.

The target platform is supposed to support classes and instances with
**single inheritance**. Instances of user-defined classes are mapped
to the ``Instance`` type, whose ``_superclass`` attribute indicates
the base class of the instance. At the very beginning of the
inheritance hierarchy there is the ``Root`` object, i.e. the common
base class between all instances; if the target platform has the
notion of a common base class too, the backend can choose to map the
``Root`` class to its native equivalent.

Object of ``Instance`` type can have attributes and methods:
attributes are got and set by the ``oogetfield`` and ``oosetfield``
operations, while method calls are expressed by the ``oosend``
operation.

Classes are passed around using the ``Class`` type: this is a first
order class type whose only goal is to allow **runtime instantiation**
of the class. Backends that don't support this feature natively, such
as Java, may need to use some sort of placeholder instead.


Static vs. dynamic typing
+++++++++++++++++++++++++

The target platform is assumed to be **statically typed**, i.e.  the
type of each object is known at compile time.

As usual, it is possible to convert an object from type to type only
under certain conditions; there is a number of predefined conversions
between primitive types such as from ``Bool`` to ``Signed`` or from
``Signed`` to ``Float``. For each one of these conversions there is a
corresponding low level operation, such as ``cast_bool_to_int`` and
``cast_int_to_float``.

Moreover it is possible to cast instances of a class up and down the
inheritance hierarchy with the ``ooupcast`` and ``oodowncast`` low
level operations. Implicit upcasting is not allowed, so you really
need to do a ``ooupcast`` for converting from a subclass to a
superclass.

With this design statically typed backends can trivially insert
appropriate casts when needed, while dynamically typed backends can
simply ignore some of the operation such as ``ooupcast`` and
``oodowncast``. Backends that supports implicit upcasting, such as CLI
and Java, can simply ignore only ``ooupcast``.

Object model
++++++++++++

The object model implemented by ootype is quite Java-like. The
following is a list of key features of the ootype object model which
have a direct correspondence in the Java or .NET object model:

  - classes have a static set of strongly typed methods and
    attributes;

  - methods can be overriden in subclasses; every method is "virtual"
    (i.e., can be overridden); methods can be "abstract" (i.e., need
    to be overridden in subclasses);

  - classes support single inheritance; all classes inherit directly
    or indirectly from the ROOT class;

  - there is some support for method overloading. This feature is not
    used by the RTyper itself because RPython doesn't support method
    overloading, but it is used by the GenCLI backend for offering
    access to the native .NET libraries (see XXX);

  - all classes, attributes and methods are public: ootype is only
    used internally by the translator, so there is no need to enforce
    accessibility rules;

  - classes and functions are first-class order objects: this feature
    can be easily simulated by backends for platforms on which it is not
    a native feature;

  - there is a set of `built-in types`_ offering standard features.

Exception handling
++++++++++++++++++

Since flow graphs are meant to be used also for very low level
backends such as C, they are quite unstructured: this means that the
target platform doesn't need to have a native exception handling
mechanism, since at the very least the backend can handle exceptions
just like ``genc`` does.

By contrast we know that most of high level platforms natively support
exception handling, so *ootypesystem* is designed to let them to use
it. In particular the exception instances are typed with the
``Instance`` type, so the usual inheritance exception hierarchy is
preserved and the native way to catch exception should just work.

.. `built-in types`_

Built-in types
++++++++++++++

It seems reasonable to assume high level platforms to provide built-in
facilities for common types such as *lists* or *hashtables*.

RPython standard types such as ``List`` and ``Dict`` are implemented
on top of these common types; at the moment of writing there are six
built-in types:

  - **String**: self-descriptive

  - **StringBuilder**: used for dynamic building of string

  - **List**: a variable-sized, homogeneous list of object

  - **Dict**: a hashtable of homogeneous keys and values

  - **CustomDict**: same as dict, but with custom equal and hash
    functions

  - **DictItemsIterator**: a helper class for iterating over the
    elements of a ``Dict``


Each of these types is a subtype of ``BuiltinADTType`` and has set of
ADT (Abstract Data Type) methods (hence the name of the base class)
for being manipulated. Examples of ADT methods are ``ll_length`` for
``List`` and ``ll_get`` for ``Dict``.

From the backend point of view an instance of a built-in types is
treated exactly as a plain ``Instance``, so usually no special-casing
is needed. The backend is supposed to provide a bunch of classes
wrapping the native ones in order to provide the right signature and
semantic for the ADT methods.

As an alternative, backends can special-case the ADT types to map them
directly to the native equivalent, translating the method names
on-the-fly at compile time.

Generics
++++++++

Some target platforms offer native support for **generics**, i.e.
classes that can be parametrized on types, not only values. For
example, if one wanted to create a list using generics, a possible
declaration would be to say ``List<T>``, where ``T`` represented the
type.  When instantiated, one could create ``List<Integer>`` or
``List<Animal>``. The list is then treated as a list of whichever type
is specified.

Each subclass of ``BuiltinADTTypes`` defines a bunch of type
parameters by creating some class level placeholder in the form of
``PARAMNAME_T``; then it fills up the ``_GENERIC_METHODS`` attribute
by defining the signature of each of the ADT methods using those
placeholders in the appropriate places. As an example, here is an
extract of *ootypesystem*'s List type::

    class List(BuiltinADTType):
        # placeholders for types
        SELFTYPE_T = object()
        ITEMTYPE_T = object()

        ...

        def _init_methods(self):
            # 'ITEMTYPE_T' is used as a placeholder for indicating
            # arguments that should have ITEMTYPE type. 'SELFTYPE_T' indicates 'self'

            self._GENERIC_METHODS = frozendict({
                "ll_length": Meth([], Signed),
                "ll_getitem_fast": Meth([Signed], self.ITEMTYPE_T),
                "ll_setitem_fast": Meth([Signed, self.ITEMTYPE_T], Void),
                "_ll_resize_ge": Meth([Signed], Void),
                "_ll_resize_le": Meth([Signed], Void),
                "_ll_resize": Meth([Signed], Void),
            })

        ...

Thus backends that support generics can simply look for placeholders
for discovering where the type parameters are used. Backends that
don't support generics can simply use the ``Root`` class instead and
insert the appropriate casts where needed. Note that placeholders
might also stand for primitive types, which typically require more
involved casts: e.g. in Java, making wrapper objects around ints.


HighLevelOp interface
---------------------

In the absence of more extensive documentation about how RPython types are
implemented, here is the interface and intended usage of the 'hop'
argument that appears everywhere.  A 'hop' is a HighLevelOp instance,
which represents a single high-level operation that must be turned into
one or several low-level operations.

    ``hop.llops``
        A list-like object that records the low-level operations that
        correspond to the current block's high-level operations.

    ``hop.genop(opname, list_of_variables, resulttype=resulttype)``
        Append a low-level operation to ``hop.llops``.  The operation has
        the given opname and arguments, and returns the given low-level
        resulttype.  The arguments should come from the ``hop.input*()``
        functions described below.

    ``hop.gendirectcall(ll_function, var1, var2...)``
        Like hop.genop(), but produces a ``direct_call`` operation that
        invokes the given low-level function, which is automatically
        annotated with low-level types based on the input arguments.

    ``hop.inputargs(r1, r2...)``
        Reads the high-level Variables and Constants that are the
        arguments of the operation, and convert them if needed so that
        they have the specified representations.  You must provide as many
        representations as the operation has arguments.  Returns a list of
        (possibly newly converted) Variables and Constants.

    ``hop.inputarg(r, arg=i)``
        Same as inputargs(), but only converts and returns the ith
        argument.

    ``hop.inputconst(lltype, value)``
        Returns a Constant with a low-level type and value.

Manipulation of HighLevelOp instances (this is used e.g. to insert a
'self' implicit argument to translate method calls):

    ``hop.copy()``
        Returns a fresh copy that can be manipulated with the functions
        below.

    ``hop.r_s_popfirstarg()``
        Removes the first argument of the high-level operation.  This
        doesn't really changes the source SpaceOperation, but modifies
        'hop' in such a way that methods like inputargs() no longer see
        the removed argument.

    ``hop.v_s_insertfirstarg(v_newfirstarg, s_newfirstarg)``
        Insert an argument in front of the hop.  It must be specified by
        a Variable (as in calls to hop.genop()) and a corresponding
        annotation.

    ``hop.swap_fst_snd_args()``
        Self-descriptive.

Exception handling:

    ``hop.has_implicit_exception(cls)``
        Checks if hop is in the scope of a branch catching the exception 
        'cls'.  This is useful for high-level operations like 'getitem'
        that have several low-level equivalents depending on whether they
        should check for an IndexError or not.  Calling
        has_implicit_exception() also has a side-effect: the rtyper
        records that this exception is being taken care of explicitly.

    ``hop.exception_is_here()``
        To be called with no argument just before a llop is generated.  It
        means that the llop in question will be the one that should be
        protected by the exception catching.  If has_implicit_exception()
        was called before, then exception_is_here() verifies that *all*
        except links in the graph have indeed been checked for with an
        has_implicit_exception().  This is not verified if
        has_implicit_exception() has never been called -- useful for
        'direct_call' and other operations that can just raise any exception.

    ``hop.exception_cannot_occur()``
        The RTyper normally verifies that exception_is_here() was really
        called once for each high-level operation that is in the scope of
        exception-catching links.  By saying exception_cannot_occur(),
        you say that after all this particular operation cannot raise
        anything.  (It can be the case that unexpected exception links are
        attached to flow graphs; e.g. any method call within a
        ``try:finally:`` block will have an Exception branch to the finally
        part, which only the RTyper can remove if exception_cannot_occur()
        is called.)


.. _LLInterpreter:

The LLInterpreter
-----------------

The LLInterpreter is a simple piece of code that is able to interpret flow
graphs. This is very useful for testing purposes, especially if you work on
the RPython Typer. The most useful interface for it is the ``interpret``
function in the file `rpython/rtyper/test/test_llinterp.py`_. It takes as
arguments a function and a list of arguments with which the function is
supposed to be called. Then it generates the flow graph, annotates it
according to the types of the arguments you passed to it and runs the
LLInterpreter on the result. Example::

    def test_invert():
        def f(x):
            return ~x
        res = interpret(f, [3])
        assert res == ~3

Furthermore there is a function ``interpret_raises`` which behaves much like
``py.test.raises``. It takes an exception as a first argument, the function to
be called as a second and the list of function arguments as a third. Example::

    def test_raise():
        def raise_exception(i):
            if i == 42:
                raise IndexError
            elif i == 43:
                raise ValueError
            return i
        res = interpret(raise_exception, [41])
        assert res == 41
        interpret_raises(IndexError, raise_exception, [42])
        interpret_raises(ValueError, raise_exception, [43])

By default the ``interpret`` and ``interpret_raises`` functions use
the low-level typesystem. If you want to use the object oriented one
you have to set the ``type_system`` parameter to the string
``'ootype'``::

    def test_invert():
        def f(x):
            return ~x
        res = interpret(f, [3], type_system='ootype')
        assert res == ~3

.. _annotator: translation.html#the-annotation-pass

.. include:: _ref.txt
