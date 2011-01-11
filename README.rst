=========
ConvUtils
=========

ConvUtils provides a small library of convenience functions for dealing
with a variety of tasks, such as creating CSV readers and writers, and
convenient data structures, such as a two-way dictionary.

This package provides two libraries: ``convutils`` and ``convstructs``.


``convutils``
=============

``convutils`` provides the following functions:

  * ``make_csv_reader`` creates a ``csv.DictReader`` or ``csv.Reader``
    instance with the convenience of the user not having to explicitly
    specify the CSV dialect
  * ``make_csv_dict_writer`` creates a ``csv.DictWriter`` instance with
    the convenience of not having to manually enter the header row
    yourself
  * ``append_to_file_base_name`` will return a modified file name given
    an original one and a string between the base name and the extension
    (e.g., ``append_to_file_base_name('myfile.txt', '-2')`` returns
    ``'myfile-2.txt'``)
  * ``count_lines`` counts the number of lines in a file
  * ``split_file_by_parts`` takes one large file and splits it into new
    files, the maximum number of which is given by the user
  * ``split_file_by_num_lines`` takes one large file and splits it into
    new file, the maximum number of lines in each being defined by the
    user
  * ``column_args_to_indices`` takes a string representing desired
    columns (e.g., ``'1-4,6,8'``) and converts it into actual indices
    and slices of an indexable Python sequence


``convstructs``
===============

``convstructs`` provides two convenient data structures, both
specialized subclasses of Python's ``dict``.

  * ``SortedTupleKeysDict`` is a dictionary which expects 2-tuples as
    keys, and will always sort the tuples, either when setting or
    retrieving values
  * ``TwoWaySetDict`` is a dictionary that assumes the values are sets,
    and will store a reverse lookup dictionary to tell you, for each set
    in the values that some item belongs to, the keys with which item is
    associated

