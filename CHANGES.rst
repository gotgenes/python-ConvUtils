#########
CHANGELOG
#########

v2.0
====

* Made compatible with Python 3 via 2to3 during installation.
* Dropped compatibility for Python 2 versions less than 2.7.
* Refactored code for Python 2.7 and Python 3 compatibility.
* Added dependency on `mock`_ for unit tests. This dependency is
  satisfied by the standard library for Python 3.3 and newer.
* Added unit tests for ``convutils.convutils``.
* Renamed ``ExcelTabNewlineDialect`` to ``SimpleTsvDialect``, and
  changed its quoting style to no quoting.
* Refactored ``make_csv_reader`` and ``make_simple_tsv_dict_writer`` to
  use the ``csv.excel`` dialect by default, to be more in line with the
  standard library. Added new functions ``make_simple_tsv_reader`` and
  ``make_simple_tsv_dict_writer`` for the previous functionality.
* Changed the signature of ``split_file_by_num_lines``. The function now
  accepts a filehandle instead of a file name. The parameter
  ``has_header`` has been renamed ``header``. Added two new parameters,
  ``pad_file_names`` and ``num_lines_total``. If ``pad_file_names`` is
  ``True``, the numerical portion of the output file names will be
  zero-padded. If ``num_lines_total`` is provided in addition to
  ``pad_file_names``, ``split_file_by_num_lines`` will skip counting the
  number of lines in the file, itself, which can save time.

.. _mock: http://www.voidspace.org.uk/python/mock/


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
