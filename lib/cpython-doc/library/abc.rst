:mod:`abc` --- Abstract Base Classes
====================================

.. module:: abc
   :synopsis: Abstract base classes according to PEP 3119.
.. moduleauthor:: Guido van Rossum
.. sectionauthor:: Georg Brandl
.. much of the content adapted from docstrings

**Source code:** :source:`Lib/abc.py`

--------------

This module provides the infrastructure for defining :term:`abstract base
classes <abstract base class>` (ABCs) in Python, as outlined in :pep:`3119`; see the PEP for why this
was added to Python. (See also :pep:`3141` and the :mod:`numbers` module
regarding a type hierarchy for numbers based on ABCs.)

The :mod:`collections` module has some concrete classes that derive from
ABCs; these can, of course, be further derived. In addition the
:mod:`collections.abc` submodule has some ABCs that can be used to test whether
a class or instance provides a particular interface, for example, is it
hashable or a mapping.


This module provides the following class:

.. class:: ABCMeta

   Metaclass for defining Abstract Base Classes (ABCs).

   Use this metaclass to create an ABC.  An ABC can be subclassed directly, and
   then acts as a mix-in class.  You can also register unrelated concrete
   classes (even built-in classes) and unrelated ABCs as "virtual subclasses" --
   these and their descendants will be considered subclasses of the registering
   ABC by the built-in :func:`issubclass` function, but the registering ABC
   won't show up in their MRO (Method Resolution Order) nor will method
   implementations defined by the registering ABC be callable (not even via
   :func:`super`). [#]_

   Classes created with a metaclass of :class:`ABCMeta` have the following method:

   .. method:: register(subclass)

      Register *subclass* as a "virtual subclass" of this ABC. For
      example::

        from abc import ABCMeta

        class MyABC(metaclass=ABCMeta):
            pass

        MyABC.register(tuple)

        assert issubclass(tuple, MyABC)
        assert isinstance((), MyABC)

      .. versionchanged:: 3.3
         Returns the registered subclass, to allow usage as a class decorator.

   You can also override this method in an abstract base class:

   .. method:: __subclasshook__(subclass)

      (Must be defined as a class method.)

      Check whether *subclass* is considered a subclass of this ABC.  This means
      that you can customize the behavior of ``issubclass`` further without the
      need to call :meth:`register` on every class you want to consider a
      subclass of the ABC.  (This class method is called from the
      :meth:`__subclasscheck__` method of the ABC.)

      This method should return ``True``, ``False`` or ``NotImplemented``.  If
      it returns ``True``, the *subclass* is considered a subclass of this ABC.
      If it returns ``False``, the *subclass* is not considered a subclass of
      this ABC, even if it would normally be one.  If it returns
      ``NotImplemented``, the subclass check is continued with the usual
      mechanism.

      .. XXX explain the "usual mechanism"


   For a demonstration of these concepts, look at this example ABC definition::

      class Foo:
          def __getitem__(self, index):
              ...
          def __len__(self):
              ...
          def get_iterator(self):
              return iter(self)

      class MyIterable(metaclass=ABCMeta):

          @abstractmethod
          def __iter__(self):
              while False:
                  yield None

          def get_iterator(self):
              return self.__iter__()

          @classmethod
          def __subclasshook__(cls, C):
              if cls is MyIterable:
                  if any("__iter__" in B.__dict__ for B in C.__mro__):
                      return True
              return NotImplemented

      MyIterable.register(Foo)

   The ABC ``MyIterable`` defines the standard iterable method,
   :meth:`__iter__`, as an abstract method.  The implementation given here can
   still be called from subclasses.  The :meth:`get_iterator` method is also
   part of the ``MyIterable`` abstract base class, but it does not have to be
   overridden in non-abstract derived classes.

   The :meth:`__subclasshook__` class method defined here says that any class
   that has an :meth:`__iter__` method in its :attr:`__dict__` (or in that of
   one of its base classes, accessed via the :attr:`__mro__` list) is
   considered a ``MyIterable`` too.

   Finally, the last line makes ``Foo`` a virtual subclass of ``MyIterable``,
   even though it does not define an :meth:`__iter__` method (it uses the
   old-style iterable protocol, defined in terms of :meth:`__len__` and
   :meth:`__getitem__`).  Note that this will not make ``get_iterator``
   available as a method of ``Foo``, so it is provided separately.


The :mod:`abc` module also provides the following decorators:

.. decorator:: abstractmethod(function)

   A decorator indicating abstract methods.

   Using this decorator requires that the class's metaclass is :class:`ABCMeta`
   or is derived from it.  A class that has a metaclass derived from
   :class:`ABCMeta` cannot be instantiated unless all of its abstract methods
   and properties are overridden.  The abstract methods can be called using any
   of the normal 'super' call mechanisms.  :func:`abstractmethod` may be used
   to declare abstract methods for properties and descriptors.

   Dynamically adding abstract methods to a class, or attempting to modify the
   abstraction status of a method or class once it is created, are not
   supported.  The :func:`abstractmethod` only affects subclasses derived using
   regular inheritance; "virtual subclasses" registered with the ABC's
   :meth:`register` method are not affected.

   When :func:`abstractmethod` is applied in combination with other method
   descriptors, it should be applied as the innermost decorator, as shown in
   the following usage examples::

      class C(metaclass=ABCMeta):
          @abstractmethod
          def my_abstract_method(self, ...):
              ...
          @classmethod
          @abstractmethod
          def my_abstract_classmethod(cls, ...):
              ...
          @staticmethod
          @abstractmethod
          def my_abstract_staticmethod(...):
              ...

          @property
          @abstractmethod
          def my_abstract_property(self):
              ...
          @my_abstract_property.setter
          @abstractmethod
          def my_abstract_property(self, val):
              ...

          @abstractmethod
          def _get_x(self):
              ...
          @abstractmethod
          def _set_x(self, val):
              ...
          x = property(_get_x, _set_x)

   In order to correctly interoperate with the abstract base class machinery,
   the descriptor must identify itself as abstract using
   :attr:`__isabstractmethod__`. In general, this attribute should be ``True``
   if any of the methods used to compose the descriptor are abstract. For
   example, Python's built-in property does the equivalent of::

      class Descriptor:
          ...
          @property
          def __isabstractmethod__(self):
              return any(getattr(f, '__isabstractmethod__', False) for
                         f in (self._fget, self._fset, self._fdel))

   .. note::

      Unlike Java abstract methods, these abstract
      methods may have an implementation. This implementation can be
      called via the :func:`super` mechanism from the class that
      overrides it.  This could be useful as an end-point for a
      super-call in a framework that uses cooperative
      multiple-inheritance.


.. decorator:: abstractclassmethod(function)

   A subclass of the built-in :func:`classmethod`, indicating an abstract
   classmethod. Otherwise it is similar to :func:`abstractmethod`.

   Usage::

      class C(metaclass=ABCMeta):
          @abstractclassmethod
          def my_abstract_classmethod(cls, ...):
              ...

   .. versionadded:: 3.2
   .. deprecated:: 3.3
       Use :class:`classmethod` with :func:`abstractmethod` instead


.. decorator:: abstractstaticmethod(function)

   A subclass of the built-in :func:`staticmethod`, indicating an abstract
   staticmethod. Otherwise it is similar to :func:`abstractmethod`.

   Usage::

      class C(metaclass=ABCMeta):
          @abstractstaticmethod
          def my_abstract_staticmethod(...):
              ...

   .. versionadded:: 3.2
   .. deprecated:: 3.3
       Use :class:`staticmethod` with :func:`abstractmethod` instead


.. decorator:: abstractproperty(fget=None, fset=None, fdel=None, doc=None)

   A subclass of the built-in :func:`property`, indicating an abstract property.

   Using this function requires that the class's metaclass is :class:`ABCMeta`
   or is derived from it. A class that has a metaclass derived from
   :class:`ABCMeta` cannot be instantiated unless all of its abstract methods
   and properties are overridden. The abstract properties can be called using
   any of the normal 'super' call mechanisms.

   Usage::

      class C(metaclass=ABCMeta):
          @abstractproperty
          def my_abstract_property(self):
              ...

   This defines a read-only property; you can also define a read-write abstract
   property using the 'long' form of property declaration::

      class C(metaclass=ABCMeta):
          def getx(self): ...
          def setx(self, value): ...
          x = abstractproperty(getx, setx)

   .. deprecated:: 3.3
       Use :class:`property` with :func:`abstractmethod` instead


.. rubric:: Footnotes

.. [#] C++ programmers should note that Python's virtual base class
   concept is not the same as C++'s.
