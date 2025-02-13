.. _distutils-index:

###############################
  Distributing Python Modules
###############################

:Authors: Greg Ward, Anthony Baxter
:Email: distutils-sig@python.org
:Release: |version|
:Date: |today|

This document describes the Python Distribution Utilities ("Distutils") from
the module developer's point of view, describing how to use the Distutils to
make Python modules and extensions easily available to a wider audience with
very little overhead for build/release/install mechanics.

.. deprecated:: 3.3
   :mod:`packaging` replaces Distutils.  See :ref:`packaging-index` and
   :ref:`packaging-install-index`.

.. toctree::
   :maxdepth: 2

   introduction.rst
   setupscript.rst
   configfile.rst
   sourcedist.rst
   builtdist.rst
   packageindex.rst
   uploading.rst
   examples.rst
   extending.rst
   commandref.rst
   apiref.rst

Another document describes how to install modules and extensions packaged
following the above guidelines:

.. toctree::

   install.rst
