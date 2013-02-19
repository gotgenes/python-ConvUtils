#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2012 Christopher D. Lasher
#
# This software is released under the MIT License. Please see
# LICENSE.txt for details.


"""Tests for utils"""

from StringIO import StringIO
import sys
import unittest

try:
    from unittest.mock import call, MagicMock, patch
except ImportError:
    from mock import call, MagicMock, patch

from convutils import utils


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
        result = list(utils.make_csv_reader(self.testfile1))
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
        result = list(utils.make_simple_tsv_reader(
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


    def test_no_header(self):
        result = list(utils.make_csv_reader(self.testfile1,
                                                header=False))
        expected = [
            ['col1', 'col2', 'col3'],
            ['this', 'value\tis', 'awesome'],
            ['this', 'one\tis', 'too']
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
        writer = utils.make_csv_dict_writer(
                self.csvfile, self.fieldnames)
        writer.writerows(self.rows)
        self.csvfile.seek(0)
        result = self.csvfile.read()
        expected = 'col1,col2\r\n1,2\r\n3,4\r\n'
        self.assertEqual(result, expected)


    def test_make_simple_tsv_dict_writer(self):
        writer = utils.make_simple_tsv_dict_writer(
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
        result = utils.append_to_file_base_name(file_name, '-ok')
        self.assertEqual(result, 'a-ok.file')


class TestCountLines(unittest.TestCase):
    """Tests for count_lines()"""

    def test_count_lines(self):
        testfile = StringIO('1\n2\n3\n')
        result = utils.count_lines(testfile)
        self.assertEqual(result, 3)


class SplitFileTestCase(unittest.TestCase):
    """Base class for testing file splitting."""

    def _create_fake_file(self, num_lines, filename='testfile.txt'):
        lines = ['{}\n'.format(i) for i in range(1, num_lines + 1)]
        testfile = StringIO(''.join(lines))
        testfile.name = filename
        return lines, testfile


    def setUp(self):
        self.lines, self.testfile = self._create_fake_file(20)


    def tearDown(self):
        FAKEOPEN.reset_mock()
        FAKEFILE.reset_mock()


    def _make_expected_open_calls(self, name_template, num_files):
        return [
            call(name_template.format(i), 'w') for i in
            range(1, num_files + 1)
        ]


    def _make_expected_write_calls(self, lines, lines_per_file,
                                   header=False):
        expected_write_calls = []
        start_line = 1 if header else 0
        for i in range(start_line, len(lines), lines_per_file):
            if header:
                expected_write_calls.append(call.write(self.lines[0]))
            expected_write_calls.append(
                    call.writelines(lines[i:i+lines_per_file]))
            expected_write_calls.append(call.close())
        return expected_write_calls


    def _test_expected_calls_made(
            self,
            lines,
            num_output_files_expected,
            max_lines_per_file,
            outfile_template='testfile-{}.txt',
            header=False
        ):
        expected_open_calls = self._make_expected_open_calls(
                outfile_template, num_output_files_expected)
        self.assertEqual(FAKEOPEN.call_args_list, expected_open_calls)
        expected_write_calls = self._make_expected_write_calls(
                lines, max_lines_per_file, header)
        self.assertEqual(FAKEFILE.method_calls, expected_write_calls)


class TestReadFileChunk(SplitFileTestCase):
    """Tests for _read_file_chunk()"""

    def test_read_three(self):
        result = utils._read_file_chunk(self.testfile, 3)
        expected = self.lines[:3]
        self.assertEqual(result, expected)


    def test_eof(self):
        self.testfile.read()
        result = utils._read_file_chunk(self.testfile, 10)
        self.assertEqual(result, [])


    def test_ask_for_more_lines(self):
        result = utils._read_file_chunk(self.testfile, 30)
        expected = self.lines
        self.assertEqual(result, expected)


@patch(BUILTIN_OPEN, FAKEOPEN)
class TestSplitFileByNumLines(SplitFileTestCase):
    """Tests for split_file_by_num_lines()"""

    def test_no_split(self):
        utils.split_file_by_num_lines(self.testfile, 20)
        FAKEOPEN.assert_called_once_with('testfile-1.txt', 'w')
        self.assertEqual(
                FAKEFILE.method_calls,
                [call.writelines(self.lines), call.close()]
        )


    def test_split_by_five(self):
        utils.split_file_by_num_lines(self.testfile, 5)
        self._test_expected_calls_made(self.lines, 4, 5)


    def test_header(self):
        utils.split_file_by_num_lines(self.testfile, 5,
                                          header=True)
        self._test_expected_calls_made(self.lines, 4, 5, header=True)


    def test_padding(self):
        utils.split_file_by_num_lines(self.testfile, 2,
                                          pad_file_names=True)
        self._test_expected_calls_made(self.lines, 10, 2,
                                       'testfile-{:02}.txt')


    def test_padding_with_num_total_lines(self):
        utils.split_file_by_num_lines(
                self.testfile,
                2,
                pad_file_names=True,
                num_lines_total=20
        )
        self._test_expected_calls_made(self.lines, 10, 2,
                                       'testfile-{:02}.txt')


@patch(BUILTIN_OPEN, FAKEOPEN)
class TestSplitFileByParts(SplitFileTestCase):
    """Tests for split_file_by_parts()"""

    def test_one_part(self):
        utils.split_file_by_parts(self.testfile, 1)
        FAKEOPEN.assert_called_once_with('testfile-1.txt', 'w')
        self.assertEqual(
                FAKEFILE.method_calls,
                [call.writelines(self.lines), call.close()]
        )


    def test_two_parts(self):
        utils.split_file_by_parts(self.testfile, 2)
        self._test_expected_calls_made(self.lines, 2, 10)


    def test_three_parts(self):
        utils.split_file_by_parts(self.testfile, 3)
        self._test_expected_calls_made(self.lines, 3, 7)


    def test_twelve_parts(self):
        utils.split_file_by_parts(self.testfile, 12)
        self._test_expected_calls_made(self.lines, 10, 2)


    def test_ten_lines_six_parts(self):
        lines, testfile = self._create_fake_file(10)
        utils.split_file_by_parts(testfile, 6)
        self._test_expected_calls_made(lines, 5, 2)


    def test_header(self):
        utils.split_file_by_parts(self.testfile, 3, header=True)
        self._test_expected_calls_made(self.lines, 3, 7, header=True)


class TestColumnArgsToIndices(unittest.TestCase):
    """Tests for column_args_to_indices()"""

    def test_column_args_to_indices(self):
        cases_and_expecteds = (
            ('5', [4]),
            ('1-5', [slice(0, 5)]),
            ('1,3,5-10', [0, 2, slice(4, 10)])
        )
        for case, expected in cases_and_expecteds:
            result = utils.column_args_to_indices(case)
            self.assertEqual(result, expected)


class TestCumsum(unittest.TestCase):
    """Tests for cumsum()"""

    def test_cumsum(self):
        case = [5, 8, 3, 3, 7]
        expected = [5, 13, 16, 19, 26]
        result = list(utils.cumsum(case))
        self.assertEqual(result, expected)


    def test_no_items(self):
        case = []
        expected = []
        result = list(utils.cumsum(case))
        self.assertEqual(result, expected)


if __name__ == '__main__':
     unittest.main()

