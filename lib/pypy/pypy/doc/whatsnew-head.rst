======================
What's new in PyPy 2.0
======================

.. this is a revision shortly after release-2.0-beta1
.. startrev: 0e6161a009c6

.. branch: split-rpython
Split rpython and pypy into seperate directories

.. branch: callback-jit
Callbacks from C are now better JITted

.. branch: fix-jit-logs

.. branch: remove-globals-in-jit

.. branch: length-hint
Implement __lenght_hint__ according to PEP 424

.. branch: numpypy-longdouble
Long double support for numpypy

.. branch: numpypy-disable-longdouble
Since r_longdouble support is missing, disable all longdouble and derivative
dtypes using ENABLED_LONG_DOUBLE = False

.. branch: numpypy-real-as-view
Convert real, imag from ufuncs to views. This involves the beginning of
view() functionality

.. branch: indexing-by-array
Adds indexing by scalar, adds int conversion from scalar and single element array,
fixes compress, indexing by an array with a smaller shape and the indexed object.

.. branch: str-dtype-improvement
Allow concatenation of str and numeric arrays

.. branch: signatures
Improved RPython typing

.. branch: rpython-bytearray
Rudimentary support for bytearray in RPython

.. branches we don't care about
.. branch: autoreds
.. branch: reflex-support
.. branch: kill-faking
.. branch: improved_ebnfparse_error
.. branch: task-decorator
.. branch: fix-e4fa0b2
.. branch: win32-fixes
.. branch: numpy-unify-methods
.. branch: fix-version-tool
.. branch: popen2-removal
.. branch: pickle-dumps
.. branch: scalar_get_set

.. branch: release-2.0-beta1

.. branch: remove-PYPY_NOT_MAIN_FILE

.. branch: missing-jit-operations

.. branch: fix-lookinside-iff-oopspec
Fixed the interaction between two internal tools for controlling the JIT.

.. branch: inline-virtualref-2
Better optimized certain types of frame accesses in the JIT, particularly
around exceptions that escape the function they were raised in.

.. branch: missing-ndarray-attributes
Some missing attributes from ndarrays

.. branch: cleanup-tests
Consolidated the lib_pypy/pypy_test and pypy/module/test_lib_pypy tests into
one directory for reduced confusion and so they all run nightly.

.. branch: unquote-faster
.. branch: urlparse-unquote-faster

.. branch: signal-and-thread
Add "__pypy__.thread.signals_enabled", a context manager. Can be used in a
non-main thread to enable the processing of signal handlers in that thread.

.. branch: coding-guide-update-rlib-refs
.. branch: rlib-doc-rpython-refs
.. branch: clean-up-remaining-pypy-rlib-refs

.. branch: enumerate-rstr
Support enumerate() over rstr types.

.. branch: cleanup-numpypy-namespace
Cleanup _numpypy and numpypy namespaces to more closely resemble numpy.

.. branch: kill-flowobjspace
Random cleanups to hide FlowObjSpace from public view.

.. branch: vendor-rename
Remove minor verison number from lib-python dirs to simplify stdlib upgrades.

.. branch: jitframe-on-heap
Moves optimized JIT frames from stack to heap. As a side effect it enables
stackless to work well with the JIT on PyPy. Also removes a bunch of code from
the GC which fixes cannot find gc roots.

.. branch: pycon2013-doc-fixes
Documentation fixes after going through the docs at PyCon 2013 sprint.

.. branch: extregistry-refactor

.. branch: remove-list-smm
