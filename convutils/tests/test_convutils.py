#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2012 Christopher D. Lasher
#
# This software is released under the MIT License. Please see
# LICENSE.txt for details.


"""Tests for convutils"""

import csv
from StringIO import StringIO
import sys
import unittest

try:
    from unittest.mock import call, MagicMock, patch
except ImportError:
    from mock import call, MagicMock, patch

from convutils import convutils


if sys.version_info[0] < 3:
    BUILTIN_OPEN = '__builtin__.open'
else:
    BUILTIN_OPEN = 'builtins.open'

FAKEFILE = MagicMock()
FAKEOPEN = MagicMock(return_value=FAKEFILE)


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


class SplitFileTestCase(unittest.TestCase):
    """Base class for testing file splitting."""

    def setUp(self):
        self.lines = ['{}\n'.format(i) for i in range(1, 21)]
        self.testfile = StringIO(''.join(self.lines))
        self.testfile.name = 'testfile.txt'


class TestReadFileChunk(SplitFileTestCase):
    """Tests for _read_file_chunk()"""

    def test_read_three(self):
        result = convutils._read_file_chunk(self.testfile, 3)
        expected = self.lines[:3]
        self.assertEqual(result, expected)


    def test_eof(self):
        self.testfile.read()
        result = convutils._read_file_chunk(self.testfile, 10)
        self.assertEqual(result, [])


    def test_ask_for_more_lines(self):
        result = convutils._read_file_chunk(self.testfile, 30)
        expected = self.lines
        self.assertEqual(result, expected)


@patch(BUILTIN_OPEN, FAKEOPEN)
class TestSplitFileByNumLines(SplitFileTestCase):
    """Tests for split_file_by_num_lines()"""

    def tearDown(self):
        FAKEOPEN.reset_mock()
        FAKEFILE.reset_mock()


    def _make_expected_write_calls(self, lines_per_file):
        expected_write_calls = []
        for i in range(0, len(self.lines), lines_per_file):
            expected_write_calls.append(
                    call.writelines(self.lines[i:i+lines_per_file]))
            expected_write_calls.append(call.close())
        return expected_write_calls


    def test_no_split(self):
        convutils.split_file_by_num_lines(self.testfile, 20)
        FAKEOPEN.assert_called_once_with('testfile-1.txt', 'w')
        FAKEFILE.assert_has_calls([call.writelines(self.lines)])


    def test_split_by_five(self):
        convutils.split_file_by_num_lines(self.testfile, 5)
        FAKEOPEN.assert_has_calls([
            call('testfile-{}.txt'.format(i), 'w') for i in
            range(1, 5)
        ])
        expected_write_calls = self._make_expected_write_calls(5)
        FAKEFILE.assert_has_calls(expected_write_calls)


    def test_header(self):
        convutils.split_file_by_num_lines(self.testfile, 5,
                                          header=True)
        expected_write_calls = []
        for i in range(1, len(self.lines), 5):
            expected_write_calls.append(call.write(self.lines[0]))
            expected_write_calls.append(
                    call.writelines(self.lines[i:i+5]))
            expected_write_calls.append(call.close())
        FAKEFILE.assert_has_calls(expected_write_calls)


    def test_padding(self):
        convutils.split_file_by_num_lines(self.testfile, 2,
                                          pad_file_names=True)
        FAKEOPEN.assert_has_calls([
            call('testfile-{:02}.txt'.format(i), 'w') for i in
            range(1, 11)
        ])
        expected_write_calls = self._make_expected_write_calls(2)
        FAKEFILE.assert_has_calls(expected_write_calls)


    def test_padding_with_num_total_lines(self):
        convutils.split_file_by_num_lines(
                self.testfile,
                2,
                pad_file_names=True,
                num_lines_total=20
        )
        FAKEOPEN.assert_has_calls([
            call('testfile-{:02}.txt'.format(i), 'w') for i in
            range(1, 11)
        ])
        expected_write_calls = self._make_expected_write_calls(2)
        FAKEFILE.assert_has_calls(expected_write_calls)


if __name__ == '__main__':
    unittest.main()
