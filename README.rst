*********
ConvUtils
*********

ConvUtils provides a small library of convenience functions for dealing
with a variety of tasks, such as creating CSV readers and writers, and
convenient data structures, such as a two-way dictionary.

This package provides two modules: ``utils`` and ``structs``.
Typically, the user will want to import one or the other, e.g.::

  from convutils import utils


#############
``utils``
#############

``utils`` provides the following classes:

* ``SimpleTsvDialect`` is similar to the ``csv.excel_tab`` dialect, but
  uses the newline character (``'\n'``) as the line separator, and does
  no special quoting, giving a more Unix-friendly tsv (tab-separated
  values) format. (*New in v2.0: formerly ExcelTabNewlineDialect.*)

``utils`` also provides the following functions:

* ``make_csv_reader`` creates a ``csv.DictReader`` or ``csv.Reader``
  instance with the convenience of the user not having to explicitly
  specify the CSV dialect.
* ``make_simple_tsv_reader`` is similar to ``make_csv_reader``, but
  always uses ``SimpleTsvDialect``. (*New in v2.0.*)
* ``make_csv_dict_writer`` creates a ``csv.DictWriter`` instance with
  the convenience of not having to manually enter the header row
  yourself; uses ``csv.excel`` as the dialect, by default.
* ``make_simple_tsv_dict_writer`` is similar to
  ``make_csv_dict_writer``, but uses the ``SimpleTsvDialect`` instead.
  (*New in v2.0.*)
* ``append_to_file_base_name`` will return a modified file name given
  an original one and a string between the base name and the extension
  (e.g., ``append_to_file_base_name('myfile.txt', '-2')`` returns
  ``'myfile-2.txt'``).
* ``count_lines`` counts the number of lines in a file.
* ``split_file_by_parts`` takes one large file and splits it into new
  files, the maximum number of which is given by the user.
* ``split_file_by_num_lines`` takes one large file and splits it into
  new file, the maximum number of lines in each being defined by the
  user.
* ``column_args_to_indices`` takes a string representing desired
  columns (e.g., ``'1-4,6,8'``) and converts it into actual indices
  and slices of an indexable Python sequence.
* ``cumsum`` produces the cumulative sum of any iterable whose elements
  support the add operator. (*New in v1.1.*)


###############
``structs``
###############

``structs`` provides two convenient data structures, both
specialized subclasses of Python's ``dict``.

* ``SortedTupleKeysDict`` is a dictionary which expects 2-tuples as
  keys, and will always sort the tuples, either when setting or
  retrieving values.
* ``TwoWaySetDict`` is a dictionary that assumes the values are sets,
  and will store a reverse lookup dictionary to tell you, for each set
  in the values that some item belongs to, the keys with which item is
  associated.

``structs`` also provides two functions for sampling Python
dictionaries whose values are lists:

* ``sample_list_dict`` is like ``random.sample`` but for dictionaries
  whose values are lists or other enumerable, iterable container types.
  (*New in v1.1; relocated to* ``structs`` *in v2.0.*)
* ``sample_list_dict_low_mem`` is similar to ``sample_list_dict`` but
  has a lower memory consumption for larger dictionaries. (*New in
  v1.1; relocated to* ``structs`` *in v2.0.*)


############
Installation
############

Installation is easy with `pip`_; simply run ::

  pip install ConvUtils

.. _pip: http://pypi.python.org/pypi/pip


############
Availability
############

* PyPI page: http://pypi.python.org/pypi/ConvUtils/
* GitHub project page: https://github.com/gotgenes/python-ConvUtils

