#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2012 Christopher D. Lasher
#
# This software is released under the MIT License. Please see
# LICENSE.txt for details.


"""Tests for convutils"""

import csv
from StringIO import StringIO
import unittest

from convutils import convutils


class TestMakeCsvReaders(unittest.TestCase):
    """Tests for make_csv_reader() and make_simple_tsv_reader()"""

    def setUp(self):
        teststring = '''\
"this","value\tis",awesome
"this","one\tis",too
'''
        header1 = '"col1","col2","col3"\n'
        header2 = 'col1\tcol2\n'
        self.testfile1 = StringIO(header1 + teststring)
        self.testfile2 = StringIO(header2 + teststring)


    def test_sniffing_comma_delim(self):
        result = list(convutils.make_csv_reader(self.testfile1))
        expected = [
            {
                'col1': 'this',
                'col2': 'value\tis',
                'col3': 'awesome'
            },
            {
                'col1': 'this',
                'col2': 'one\tis',
                'col3': 'too'
            }
        ]
        self.assertEqual(result, expected)


    def test_simple_tsv_dialect(self):
        result = list(convutils.make_simple_tsv_reader(
                self.testfile2))
        expected = [
            {
                'col1': '"this","value',
                'col2': 'is",awesome'
            },
            {
                'col1': '"this","one',
                'col2': 'is",too'
            },
        ]
        self.assertEqual(result, expected)


class TestMakeDictWriters(unittest.TestCase):
    """Tests for make_csv_dict_writer() and
    make_simple_tsv_dict_writer()

    """

    def setUp(self):
        self.csvfile = StringIO()
        self.fieldnames = ('col1', 'col2')
        self.rows = [{'col1': x, 'col2': y} for x, y in (('1', '2'),
                                                    ('3', '4'))]

    def test_make_csv_dict_writer(self):
        writer = convutils.make_csv_dict_writer(
                self.csvfile, self.fieldnames)
        writer.writerows(self.rows)
        self.csvfile.seek(0)
        result = self.csvfile.read()
        expected = 'col1,col2\r\n1,2\r\n3,4\r\n'
        self.assertEqual(result, expected)


    def test_make_simple_tsv_dict_writer(self):
        writer = convutils.make_simple_tsv_dict_writer(
                self.csvfile, self.fieldnames)
        writer.writerows(self.rows)
        self.csvfile.seek(0)
        result = self.csvfile.read()
        expected = 'col1\tcol2\n1\t2\n3\t4\n'
        self.assertEqual(result, expected)


class TestAppendToFileBaseName(unittest.TestCase):
    """Tests for append_to_file_base_name()"""

    def test_append_to_file_base_name(self):
        file_name = 'a.file'
        result = convutils.append_to_file_base_name(file_name, '-ok')
        self.assertEqual(result, 'a-ok.file')


class TestCountLines(unittest.TestCase):
    """Tests for count_lines()"""

    def test_count_lines(self):
        testfile = StringIO('1\n2\n3\n')
        result = convutils.count_lines(testfile)
        self.assertEqual(result, 3)


if __name__ == '__main__':
    unittest.main()

