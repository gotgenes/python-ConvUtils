#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2011-2013 Christopher D. Lasher
#
# This software is released under the MIT License. Please see
# LICENSE.txt for details.


"""A collection of common utilities and convenient functions."""

import bisect
import collections
import csv
import itertools
import os.path
import random


class SimpleTsvDialect(csv.excel_tab):
    """A simple tab-separated values dialect.


    This Dialect is similar to :class:`csv.excel_tab`, but uses
    ``'\\n'`` as the line terminator and does no special quoting.

    """
    lineterminator = '\n'
    quoting = csv.QUOTE_NONE


csv.register_dialect('simple_tsv', SimpleTsvDialect)


def make_csv_reader(csvfile, headers=True, dialect=None, *args,
                    **kwargs):
    """Creates a CSV reader given a CSV file.

    :param csvfile: a file handle to a CSV file
    :param headers: whether or not the file has headers
    :param dialect: a :class:`csv.Dialect` instance
    :param *args: passed on to the reader
    :param **kwargs: passed on to the reader

    """
    if dialect is None:
        try:
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
        except csv.Error:
            dialect = csv.excel
        csvfile.seek(0)
    if headers:
        csv_reader = csv.DictReader(csvfile, dialect=dialect, *args,
                **kwargs)
    else:
        csv_reader = csv.reader(csvfile, dialect=dialect, *args,
                **kwargs)
    return csv_reader


def make_simple_tsv_reader(tsvfile, headers=True, *args, **kwargs):
    """Creates a CSV reader given a CSV file.

    :param tsvfile: a file handle to a TSV file
    :param headers: whether or not the file has headers
    :param *args: passed on to the reader
    :param **kwargs: passed on to the reader

    """
    return make_csv_reader(tsvfile, headers, dialect=SimpleTsvDialect,
                           *args, **kwargs)


def make_csv_dict_writer(
        csvfile,
        fieldnames,
        *args,
        **kwargs
    ):
    """Creates a `csv.DictWriter` instance and also writes the header
    line to the file.

    :param csvfile: a file handle to a CSV file opened in write mode
    :param fieldnames: a list of field names for the columns
    :param dialect: a :class:`csv.Dialect` instance
    :param *args: passed on to :class:`csv.DictWriter()`
    :param **kwargs: passed on to :class:`csv.DictWriter()`

    """
    csv_writer = csv.DictWriter(csvfile, fieldnames, *args, **kwargs)
    csv_writer.writeheader()
    return csv_writer


def make_simple_tsv_dict_writer(
        tsvfileh,
        fieldnames,
        *args,
        **kwargs
    ):
    """Similar to :func:`make_csv_dict_writer`, but uses the
    :class:`SimpleTsvDialect` as the dialect.

    :param tsvfile: a file handle to a TSV file opened in write mode
    :param fieldnames: a list of field names for the columns
    :param *args: passed on to :class:`csv.DictWriter()`
    :param **kwargs: passed on to :class:`csv.DictWriter()`

    """
    return make_csv_dict_writer(
            tsvfileh,
            fieldnames,
            dialect=SimpleTsvDialect,
            *args,
            **kwargs
    )


def append_to_file_base_name(path, addition):
    """Extends a file's base name (the portion prior to the extension)
    with the addition.

    For example, with a path of `/foo/bar/spam.txt`, and an addition of
    `-eggs`, the returned path will be `/foo/bar/spam-eggs.txt`.

    :param path: a file path (does not have to actually exist)
    :param addition: text to append to the base name

    """
    basename, extension = os.path.splitext(path)
    new_name = '{}{}{}'.format(basename, addition, extension)
    return new_name


def count_lines(fileh):
    """Determines the number of lines in a text file.

    :param fileh: a file handle
    :returns: a non-negative integer.

    """
    num_lines = 0
    for line in fileh:
        num_lines += 1
    fileh.seek(0)
    return num_lines


def _read_file_chunk(infile, lines_per_part):
    lines = []
    for j, line in enumerate(infile):
        lines.append(line)
        if j + 1 == lines_per_part:
            break
    return lines


def split_file_by_num_lines(
        infile,
        lines_per_part,
        header=False,
        pad_file_names=False,
        num_lines_total=None
    ):
    """Divides a file into multiple files of the designated number of
    lines.

    The new files will be of the form ``<basename>-<num>.<extension>``,
    where ``<basename>`` and ``<extension>`` are derived from the
    original file, and ``<num>`` is the iteration of the split during
    which the new file was created.

    :param infile: a file handle
    :param lines_per_part: number of lines per new file (excluding header
        line, if present)
    :param header: whether the original file has a header line; if
        ``True``, header will be replicated in all new files
    :pad_file_names: provide zero-padding for the ``<num>`` in the
        output file names; requires counting all the lines in ``infile``
        unless ``num_lines_total`` is provided (default: ``False``)
    :num_lines_total: the total number of lines in ``infile``; useful
        only in conjunction with ``pad_file_names``

    """
    if pad_file_names:
        if not num_lines_total:
            num_lines_total = count_lines(infile)
        padding = len(str(num_lines_total))
        append_str = '-{{:0{}}}'.format(padding)
    else:
        append_str = '-{}'

    if header:
        header_line = infile.readline()

    outfile_num = 1
    lines = _read_file_chunk(infile, lines_per_part)
    while lines:
        outfile_name = append_to_file_base_name(
                infile.name, append_str.format(outfile_num))
        outfile = open(outfile_name, 'w')
        if header:
            outfile.write(header_line)
        outfile.writelines(lines)
        outfile.close()
        outfile_num += 1
        lines = _read_file_chunk(infile, lines_per_part)


def split_file_by_parts(
        infile,
        max_num_parts,
        header=False,
        pad_file_names=False,
        num_lines_total=None
    ):
    """Divides a file into the given number of parts.

    The new files will be of the form ``<basename>-<num>.<extension>``,
    where ``<basename>`` and ``<extension>`` are derived from the
    original file, and ``<num>`` is the iteration of the split during
    which the new file was created.

    If the number of lines of the original file (minus the header line)
    is not perfectly divisible by the number of parts, fewer parts may
    be produced (e.g., If the given file has 10 lines and 6 parts are
    asked, only 5 will be produced), and the final file may have fewer
    lines than the previous (e.g., if the original file has 156 lines
    and 5 parts are asked, the first 4 parts will have 32 lines, and the
    final fifth part will have 28).

    :param infile: a file handle
    :param num_parts: number of parts to divide the file into
    :param header: whether the original file has a header line; if
        ``True``, header will be replicated in all new files
    :pad_file_names: provide zero-padding for the ``<num>`` in the
        output file names; requires counting all the lines in ``infile``
        unless ``num_lines_total`` is provided (default: ``False``)
    :num_lines_total: the total number of lines in ``infile``; useful
        only in conjunction with ``pad_file_names``


    """
    if not num_lines_total:
        num_lines_total = count_lines(infile)
    num_lines_total = count_lines(infile)
    if header:
        num_lines_total -= 1

    lines_per_part = int(num_lines_total // max_num_parts)
    if num_lines_total % max_num_parts:
        # If we cannot perfectly divide all lines among the number of
        # parts, we'll divide the file evenly among the first n - 1
        # parts and then write out the remaining to the nth file.
        lines_per_part += 1

    split_file_by_num_lines(
            infile,
            lines_per_part,
            header,
            pad_file_names,
            num_lines_total
    )


def column_args_to_indices(col_str):
    """Converts a string representing columns to actual indices.

    Note that the text indices should be 1-indexed, and the returned
    indices and slices will be 0-indexed.

    :param col_str: a string of column designations (e.g., ``'1-4,6,8'``)
    :returns: a list of 0-based indices and slices

    """
    split_cols = col_str.split(',')
    indices = []
    for col_part in split_cols:
        if '-' in col_part:
            start, stop = col_part.split('-')
            indices.append(slice(int(start) - 1, int(stop)))
        else:
            indices.append(int(col_part) - 1)

    return indices


def cumsum(iterable):
    """Calculates the cumulative sum at each index of an iterable.

    Taken from http://stackoverflow.com/a/4844870/38140

    :param iterable: an iterable object
    :yields: the cumulative sum up to the given index

    """
    iterable = iter(iterable)
    cum_sum = 0
    for elem in iterable:
        cum_sum += elem
        yield cum_sum


def sample_list_dict(d, k):
    """Given a dictionary with lists as values, samples a given number
    of sub-elements uniformly at random.

    Consumes less memory than :func:`dict_list_random_sample`.

    :param d: a dictionary whose values are lists or other enumerable,
        iterable types
    :param k: number of sub-elements in the returned dictionary
    :returns: a dictionary with the given number of sub-elements

    """
    # Flatten the dictionary.
    flat_dict = []
    for key, val in d.items():
        for elem in val:
            flat_dict.append((key, elem))
    sampled_values = random.sample(flat_dict, k)
    sampled_d = collections.defaultdict(list)
    for key, elem in sampled_values:
        sampled_d[key].append(elem)
    return dict(sampled_d)


def sample_list_dict_low_mem(d, k):
    """Given a dictionary with lists as values, samples a given number
    of sub-elements uniformly at random.

    Consumes less memory than :func:`dict_list_random_sample` for large
    dictionaries.

    :param d: a dictionary whose values are lists or other enumerable,
        iterable types
    :param k: number of sub-elements in the returned dictionary
    :returns: a dictionary with the given number of sub-elements

    """
    # Let's say our data structure is
    #     d = {
    #         'key1': [1, 5, 9],
    #         'key2': [6, 42],
    #         'key3': [7, 9001]
    #     }
    #
    # Conceptually, we will be flattening this data structure to
    # something like
    #
    #     [('key1', 1), ('key1', 5), ('key1', 9), ('key2', 6),
    #      ('key2', 42), ('key3', 7), ('key3', 9001)]
    #
    # but we are retaining the data structure as is and instead
    # flattening the index into it.

    # Change d.keys() to list(d.keys()) in Python 3.
    keys = d.keys()                 # keys == ['key1', 'key2', 'key3']
    cum_index_bins = list(cumsum(len(v) for v in d.values()))
    # We'll shift all the indices over by one so that we can pull a
    # subtraction trick below to get the sub-index.
    cum_index_bins.insert(0, 0)     # cum_index_bins == [0, 3, 5, 7]

    total_num_elements = cum_index_bins[-1]     # total_num_elements == 7
    sampled_indices = random.sample(range(total_num_elements), k)
    sampled_d = collections.defaultdict(list)
    for index in sampled_indices:
        # say index == 3 (the fourth item, ('key2', 6) in this case)
        cum_index = bisect.bisect(cum_index_bins, index)    # cum_index == 2
        key_index = cum_index - 1   # key_index == 1
        key = keys[key_index]       # key == 'key2'
        # A trick to get the index into the list of d at that key.
        value_index = (index - cum_index_bins[key_index])   # value_index == (3 - 3) = 0
        actual_value = d[key][value_index]  # actual_value == 6
        sampled_d[key].append(actual_value)

    return dict(sampled_d)

