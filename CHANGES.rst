v2.0
====

* Made compatible with Python 3 via 2to3 during installation.
* Dropped compatibility for Python 2 versions less than 2.7.
* Refactored code for Python 2.7 and Python 3 compatibility.
* Added unit tests for ``convutils.convutils``.
* Renamed ``ExcelTabNewlineDialect`` to ``SimpleTsvDialect``, and
  changed its quoting style to no quoting.
* Refactored ``make_csv_reader`` and ``make_simple_tsv_dict_writer`` to
  use the ``csv.excel`` dialect by default, to be more in line with the
  standard library. Added new functions ``make_simple_tsv_reader`` and
  ``make_simple_tsv_dict_writer`` for the previous functionality.


v1.1 2012-03-23
===============

* Changed docstrings to use Sphinx info field lists.
* Added ``cumsum``
* Added ``sample_list_dict`` and ``sample_list_dict_low_mem``.


v1.0.1 2011-01-18
=================

* Added imports of modules into package __init__.py.


v1.0 2011-01-10
===============

* Initial release.

