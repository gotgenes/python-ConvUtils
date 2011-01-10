#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""A collection of common utilities and convenient functions."""

__author__ = 'Chris Lasher'
__email__ = 'chris DOT lasher <AT> gmail DOT com'


import csv
import os.path


class ExcelTabNewlineDialect(csv.excel_tab):
    """A dialect similar to `csv.excel_tab`, but uses `\n` as the line
    terminator.

    """
    lineterminator = '\n'


def make_csv_reader(csv_fileh, headers=True, dialect=None, *args, **kwargs):
    """Creates a CSV reader given a CSV file.

    :Parameters:
    - `csv_fileh`: a file handle to a CSV file
    - `headers`: whether or not the file has headers [DEFAULT: `True`]
    - `dialect`: a `csv.Dialect` instance
    - `*args`: passed on to the reader
    - `**kwargs`: passed on to the reader

    """
    if dialect is None:
        try:
            dialect = csv.Sniffer().sniff(csv_fileh.read(1024))
        except csv.Error:
            dialect = ExcelTabNewlineDialect
        csv_fileh.seek(0)
    if headers:
        csv_reader = csv.DictReader(csv_fileh, dialect=dialect, *args,
                **kwargs)
    else:
        csv_reader = csv.reader(csv_fileh, dialect=dialect, *args,
                **kwargs)
    return csv_reader


def make_csv_dict_writer(
        csv_fileh,
        fieldnames,
        dialect=ExcelTabNewlineDialect,
        *args,
        **kwargs
    ):
    """Creates a `csv.DictWriter` instance and also writes the header
    line to the file.

    NOTE: In Python 2.7 and 3.2, this will be obsolesced by the
    `csv.DictWriter.writeheader()` method. See
    http://bugs.python.org/issue1537721 for more detail.

    :Parameters:
    - `csv_fileh`: a file handle to a CSV file opened in write mode
    - `fieldnames`: a list of field names for the columns
    - `dialect`: a `csv.Dialect` instance [DEFAULT:
      `ExcelTabNewlineDialect`]
    - `*args`: passed on to `DictWriter()`
    - `**kwargs`: passed on to `DictWriter()`

    """
    csv_writer = csv.DictWriter(csv_fileh, fieldnames, dialect=dialect,
            *args, **kwargs)
    csv_writer.writerow(dict(zip(fieldnames, fieldnames)))
    return csv_writer


def append_to_file_base_name(path, addition):
    """Extends a file's base name (the portion prior to the extension)
    with the addition.

    For example, with a path of `/foo/bar/spam.txt`, and an addition of
    `-eggs`, the returned path will be `/foo/bar/spam-eggs.txt`.

    :Parameters:
    - `path`: a file path (does not have to actually exist)
    - `addition`: text to append to the base name

    """
    basename, extension = os.path.splitext(path)
    new_name = "%s%s%s" % (basename, addition, extension)
    return new_name


def count_lines(fileh):
    """Determines the number of lines in a text file.

    Returns a non-negative integer.

    :Parameters:
    - `fileh`: a file handle

    """
    num_lines = 0
    for line in fileh:
        num_lines += 1
    fileh.seek(0)
    return num_lines


def split_file_by_parts(filename, num_parts, has_header=False):
    """Divides a file into the given number of parts.

    The new files will be of the form BASENAME-NUM.EXTENSION, where
    BASENAME and EXTENSION are derived from the original file, and NUM
    is the iteration of the split during which the new file was created.

    If the number of lines of the original file is not perfectly
    divisible by the number of parts, fewer parts may be
    produced (e.g., If the given file has 10 lines and 6 parts are
    asked, only 5 will be produced), and the final file may have fewer
    lines than the previous (e.g., if the original file has 156 lines
    and 5 parts are asked, the first 4 parts will have 32 lines, and the
    final fifth part will have 28).

    :Parameters:
    - `filename`: the path to a file
    - `num_parts`: number of parts to divide the file into
    - `has_header`: whether the original file has a header line; if
      `True`, header will be replicated in all new files [default:
      `False`]

    """
    fileh = open(filename)
    total_lines = count_lines(fileh)
    fileh.close()
    if has_header:
        total_lines -= 1

    lines_per_part = int(total_lines / num_parts)
    if lines_per_part < 1:
        lines_per_part = 1
    if total_lines % num_parts:
        # If we cannot perfectly divide all lines among the number of
        # parts, we'll divide the file evenly among the first n - 1
        # parts and then write out the remaining to the nth file.
        lines_per_part += 1

    split_file_by_num_lines(filename, lines_per_part, has_header)


def split_file_by_num_lines(filename, lines_per_part, has_header=False):
    """Divides a file into multiple files of the designated number of
    lines.

    The new files will be of the form BASENAME-NUM.EXTENSION, where
    BASENAME and EXTENSION are derived from the original file, and NUM
    is the iteration of the split during which the new file was created.

    :Parameters:
    - `filename`: the path to a file
    - `lines_per_part`: number of lines per new file (excluding header
      line, if present)
    - `has_header`: whether the original file has a header line; if
      `True`, header will be replicated in all new files [default:
      `False`]

    """
    fileh = open(filename)
    if has_header:
        header = fileh.readline()

    i = 1
    lines = []
    for j, line in enumerate(fileh):
        lines.append(line)
        if j + 1 == lines_per_part:
            break
    while lines:
        outfile_name = append_to_file_base_name(filename, '-part%d' % (
                i))
        outfile = open(outfile_name, 'w')
        if has_header:
            outfile.write(header)
        outfile.writelines(lines)
        outfile.close()
        i += 1
        lines = []
        for j, line in enumerate(fileh):
            lines.append(line)
            if j + 1 == lines_per_part:
                break
    fileh.close()


def column_args_to_indices(col_str):
    """
    Converts a string representing columns to actual indices.

    Note that the text indices should be 1-indexed, and the returned
    indices and slices will be 0-indexed.

    :Parameters:
    - `col_str`: a string of column designations (e.g., '1-4,6,8')

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


