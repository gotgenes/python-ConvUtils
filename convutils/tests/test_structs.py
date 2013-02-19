#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2011,2013 Christopher D. Lasher
#
# This software is released under the MIT License. Please see
# LICENSE.txt for details.


"""Tests for structs.py"""

from collections import OrderedDict
import unittest

try:
    from unittest.mock import call, MagicMock, patch
except ImportError:
    from mock import call, MagicMock, patch

from convutils import structs


class TestSortedTupleKeysDict(unittest.TestCase):
    """Tests for SortedTupleKeysDict"""

    def setUp(self):
        self.d = structs.SortedTupleKeysDict((
            ((2, 1), 'x'),
            (('a',), 'waka'),
            (('c', 'b'), 'spam')
        ))


    def test_empty_init(self):
        structs.SortedTupleKeysDict()


    def test_contains(self):
        self.assertTrue((1, 2) in self.d)
        self.assertTrue((2, 1) in self.d)
        self.assertTrue(('a',) in self.d)
        self.assertTrue(('b', 'c') in self.d)
        self.assertFalse(('b', 'd') in self.d)


    def test_get(self):
        self.assertEqual(self.d.get(('c', 'b')), 'spam')
        self.assertEqual(self.d.get(('b', 'c')), 'spam')
        self.assertEqual(self.d.get(('b', 'd')), None)


    def test_getitem(self):
        self.assertEqual(self.d[('c', 'b')], 'spam')
        self.assertEqual(self.d[('b', 'c')], 'spam')
        self.assertEqual(self.d[(2, 1)], 'x')


    def test_getitem_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.d[('m', 'n')]


    def test_setitem(self):
        self.d[(2, 1)] = 'y'
        self.assertEqual(self.d[(1, 2)], 'y')
        self.d[('m', 'n')] = 5
        self.assertEqual(self.d[('m', 'n')], 5)


    def test_del(self):
        self.assertTrue((1, 2) in self.d)
        del self.d[(2, 1)]
        self.assertFalse((1, 2) in self.d)


    def test_len(self):
        self.assertEqual(len(self.d), 3)


class TwoWaySetDictTests(unittest.TestCase):

    def setize_kv_pairs(self, kv_pairs):
        """Helper function to turn sets in the values of
        dictionary key-value pairs (items) into frozensets.

        Returns a set of key-value pairs with values as frozensets.

        :param kv_pairs: the key-value pairs from dict.items()

        """
        frozen_kv_pairs = ((k, frozenset(v)) for (k, v) in kv_pairs)
        setized_kv_pairs = set(frozen_kv_pairs)
        return setized_kv_pairs


    def check_items_and_reverse_store(
            self,
            two_way_dict,
            expected_items,
            expected_reverse_store
        ):
        """Check the internals of the two-way dictionary.

        :param two_way_dict: a TwoWaySetDict instance
        :param expected_items: a set of the expected key-value pairs
        :param expected_reverse_store: a dictionary of what's expected
            for TwoWaySetDict._reverse_store()

        """
        items = self.setize_kv_pairs(two_way_dict.items())
        self.assertEqual(items, expected_items)
        self.assertEqual(
                two_way_dict._reverse_store,
                expected_reverse_store
        )


    def setUp(self):
        self.two_way_dict = structs.TwoWaySetDict()


    def test_init_empty(self):
        two_way_dict = structs.TwoWaySetDict()
        expected_items = set()
        expected_reverse_store = {}
        self.check_items_and_reverse_store(
                two_way_dict,
                expected_items,
                expected_reverse_store
        )


    def test_init_bad_items(self):
        """Check __init__ raises error if items has a value that's not a
        set.

        """
        self.assertRaises(
                ValueError,
                structs.TwoWaySetDict,
                [('a', set([1])), ('b', 2)]
        )


    def test_init_bad_kwargs(self):
        """Check __init__ raises error if **kwargs has a value that's
        not a set.

        """
        try:
            structs.TwoWaySetDict(a=set([1]), b=2)
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError not raised")


    def test_init_with_items(self):
        two_way_dict = structs.TwoWaySetDict(
                [('a', set([1])), ('b', set([1, 2]))]
        )
        expected_items = set([
                ('a', frozenset([1])),
                ('b', frozenset([1, 2]))
        ])
        expected_reverse_store = {1: set(['a', 'b']), 2: set(['b'])}
        self.check_items_and_reverse_store(
                two_way_dict,
                expected_items,
                expected_reverse_store
        )


    def test_init_with_kwargs(self):
        two_way_dict = structs.TwoWaySetDict(
                a=set([1]),
                b=set([1, 2])
        )
        expected_items = set([
                ('a', frozenset([1])),
                ('b', frozenset([1, 2]))
        ])
        expected_reverse_store = {1: set(['a', 'b']), 2: set(['b'])}
        self.check_items_and_reverse_store(
                two_way_dict,
                expected_items,
                expected_reverse_store
        )


    def test_init_with_items_and_kwargs(self):
        two_way_dict = structs.TwoWaySetDict(
                [('a', set([3]))],
                a=set([1]),
                b=set([1, 2])
        )
        expected_items = set([
                ('a', frozenset([1])),
                ('b', frozenset([1, 2]))
        ])
        expected_reverse_store = {1: set(['a', 'b']), 2: set(['b'])}
        self.check_items_and_reverse_store(
                two_way_dict,
                expected_items,
                expected_reverse_store
        )


    def test_setitem_raises_ValueError_if_not_set(self):
        try:
            self.two_way_dict['a'] = 1
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError not raised")


    def test_assign_one_entry(self):
        self.two_way_dict['a'] = set([1])
        expected_items = set([('a', frozenset([1]))])
        expected_reverse_store = {1 : set('a')}
        self.check_items_and_reverse_store(
                self.two_way_dict,
                expected_items,
                expected_reverse_store
        )


    def test_reassign_entry(self):
        self.two_way_dict['a'] = set([1, 2])
        self.two_way_dict['a'] = set([2, 3])
        expected_items = set([('a', frozenset([2, 3]))])
        expected_reverse_store = {2: set('a'), 3: set('a')}
        self.check_items_and_reverse_store(
                self.two_way_dict,
                expected_items,
                expected_reverse_store
        )


    def test_insert_multiple_entries_uncommon_value(self):
        self.two_way_dict['a'] = set([1])
        self.two_way_dict['b'] = set([2])
        expected_items = set([
                ('a', frozenset([1])),
                ('b', frozenset([2]))
        ])
        expected_reverse_store = {1: set(['a']), 2: set(['b'])}
        self.check_items_and_reverse_store(
                self.two_way_dict,
                expected_items,
                expected_reverse_store
        )


    def test_insert_multiple_entries_common_value(self):
        self.two_way_dict['a'] = set([1])
        self.two_way_dict['b'] = set([1])
        expected_items = set([
                ('a', frozenset([1])),
                ('b', frozenset([1]))
        ])
        expected_reverse_store = {1: set(['a', 'b'])}
        self.check_items_and_reverse_store(
                self.two_way_dict,
                expected_items,
                expected_reverse_store
        )


    def test_insert_entry_multiple_values(self):
        self.two_way_dict['a'] = set([1, 2])
        expected_items = set([('a', frozenset([1, 2]))])
        expected_reverse_store = {1: set(['a']), 2: set(['a'])}
        self.check_items_and_reverse_store(
                self.two_way_dict,
                expected_items,
                expected_reverse_store
        )


    def test_del_raises_KeyError(self):
        try:
            del self.two_way_dict['unknown key']
        except KeyError:
            pass
        else:
            raise AssertionError("KeyError not raised")


    def test_del_no_item(self):
        self.two_way_dict['a'] = set()
        del self.two_way_dict['a']
        expected_items = set()
        expected_reverse_store = {}
        self.check_items_and_reverse_store(
                self.two_way_dict,
                expected_items,
                expected_reverse_store
        )


    def test_del_one_key(self):
        self.two_way_dict['a'] = set([1, 2])
        del self.two_way_dict['a']
        expected_items = set()
        expected_reverse_store = {}
        self.check_items_and_reverse_store(
                self.two_way_dict,
                expected_items,
                expected_reverse_store
        )


    def test_del_multiple_keys(self):
        self.two_way_dict['a'] = set([1, 2])
        self.two_way_dict['b'] = set([2])
        del self.two_way_dict['a']
        expected_items = set([('b', frozenset([2]))])
        expected_reverse_store = {2: set(['b'])}
        self.check_items_and_reverse_store(
                self.two_way_dict,
                expected_items,
                expected_reverse_store
        )


    def test_copy(self):
        self.two_way_dict['a'] = set([1, 2])
        self.two_way_dict['b'] = set([1])
        twd_copy = self.two_way_dict.copy()
        expected_items = set([
                ('a', frozenset([1, 2])),
                ('b', frozenset([1]))
        ])
        expected_reverse_store = {1: set(['a', 'b']), 2: set(['a'])}
        self.check_items_and_reverse_store(
                twd_copy,
                expected_items,
                expected_reverse_store
        )


    def test_clear(self):
        self.two_way_dict['a'] = set([1, 2])
        self.two_way_dict['b'] = set([1])
        self.two_way_dict.clear()
        expected_items = set()
        expected_reverse_store = {}
        self.check_items_and_reverse_store(
                self.two_way_dict,
                expected_items,
                expected_reverse_store
        )


    def test_item_has_key_raises_KeyError(self):
        self.two_way_dict['a'] = set([1, 2])
        self.assertRaises(
                KeyError,
                self.two_way_dict.item_has_key,
                'unknown item',
                'a'
        )


    def test_item_has_key_false(self):
        self.two_way_dict['a'] = set([1, 2])
        self.two_way_dict['b'] = set([1])
        result = self.two_way_dict.item_has_key(2, 'b')
        self.assertEqual(result, False)


    def test_item_has_key_true(self):
        self.two_way_dict['a'] = set([1, 2])
        self.two_way_dict['b'] = set([1])
        result = self.two_way_dict.item_has_key(2, 'a')
        self.assertEqual(result, True)


    def test_get_item_keys_raises_KeyError(self):
        self.assertRaises(
                KeyError,
                self.two_way_dict.get_item_keys,
                'unknown_item'
        )


    def test_get_item_keys(self):
        self.two_way_dict['a'] = set([1, 2])
        self.two_way_dict['b'] = set([1])
        self.assertEqual(
                self.two_way_dict.get_item_keys(1),
                set(['a', 'b'])
        )
        self.assertEqual(
                self.two_way_dict.get_item_keys(2),
                set(['a'])
        )


    def test_add_item_raises_KeyError(self):
        self.assertRaises(
                KeyError,
                self.two_way_dict.add_item,
                'unknown key',
                1
        )


    def test_add_item_empty_set(self):
        self.two_way_dict['a'] = set()
        self.two_way_dict.add_item('a', 1)
        expected_items = set([('a', frozenset([1]))])
        expected_reverse_store = {1: set(['a'])}
        self.check_items_and_reverse_store(
                self.two_way_dict,
                expected_items,
                expected_reverse_store
        )


    def test_add_item_single_key(self):
        self.two_way_dict['a'] = set([1])
        self.two_way_dict.add_item('a', 2)
        expected_items = set([('a', frozenset([1, 2]))])
        expected_reverse_store = {1: set(['a']), 2: set(['a'])}
        self.check_items_and_reverse_store(
                self.two_way_dict,
                expected_items,
                expected_reverse_store
        )


    def test_add_item_multiple_keys(self):
        self.two_way_dict['a'] = set([1])
        self.two_way_dict['b'] = set([2])
        self.two_way_dict.add_item('a', 2)
        expected_items = set([
                ('a', frozenset([1, 2])),
                ('b', frozenset([2]))
        ])
        expected_reverse_store = {1: set(['a']), 2: set(['a', 'b'])}
        self.check_items_and_reverse_store(
                self.two_way_dict,
                expected_items,
                expected_reverse_store
        )


    def test_remove_item_raises_KeyError_key(self):
        self.assertRaises(
                KeyError,
                self.two_way_dict.remove_item,
                'unknown key',
                1
        )


    def test_remove_item_raises_KeyError_item(self):
        self.two_way_dict['a'] = set()
        self.assertRaises(
                KeyError,
                self.two_way_dict.remove_item,
                'a',
                1
        )


    def test_remove_item_single_key(self):
        self.two_way_dict['a'] = set([1])
        self.two_way_dict.remove_item('a', 1)
        expected_items = set([('a', frozenset())])
        expected_reverse_store = {}
        self.check_items_and_reverse_store(
                self.two_way_dict,
                expected_items,
                expected_reverse_store
        )


    def test_remove_item_multiple_keys(self):
        self.two_way_dict['a'] = set([1])
        self.two_way_dict['b'] = set([1])
        self.two_way_dict.remove_item('a', 1)
        expected_items = set([
                ('a', frozenset()),
                ('b', frozenset([1]))
        ])
        expected_reverse_store = {1: set(['b'])}


    def test_remove_item_from_all_keys_raises_KeyError(self):
        self.assertRaises(
                KeyError,
                self.two_way_dict.remove_item_from_all_keys,
                'unknown item'
        )


    def test_remove_item_from_all_keys(self):
        self.two_way_dict['a'] = set([1, 2])
        self.two_way_dict['b'] = set([1])
        self.two_way_dict.remove_item_from_all_keys(1)
        expected_items = set([
                ('a', frozenset()),
                ('b', frozenset([2]))
        ])
        expected_reverse_store = {2: set(['b'])}


    def test_len(self):
        self.assertEqual(len(self.two_way_dict), 0)
        self.two_way_dict['a'] = set([1, 2])
        self.two_way_dict['b'] = set([1])
        self.assertEqual(len(self.two_way_dict), 2)


    def test_reverse_items(self):
        self.two_way_dict['a'] = set([1, 2])
        self.two_way_dict['b'] = set([1])
        expected = [(1, set(('a', 'b'))), (2, set(('a'),))]
        result = list(self.two_way_dict.reverse_iteritems())
        self.assertEqual(result, expected)
        result = self.two_way_dict.reverse_items()
        self.assertEqual(result, expected)


    def test_has_item(self):
        self.two_way_dict['a'] = set([1, 2])
        self.two_way_dict['b'] = set([1])
        self.assertTrue(self.two_way_dict.has_item(1))
        self.assertFalse(self.two_way_dict.has_item(3))


class TestSampleListDict(unittest.TestCase):
    """Tests for sample_list_dict() and sample_list_dict_low_mem()"""

    def setUp(self):
        self.case = OrderedDict((
            ('key1', [1, 5, 9]),
            ('key2', [6, 42]),
            ('key3', [7, 9001])
        ))
        self.expected = {
            'key1': [5, 9],
            'key3': [7]
        }


    def test_sample_list_dict(self):
        sampled_values = [('key1', 5), ('key1', 9), ('key3', 7)]
        randmock = MagicMock(return_value=sampled_values)
        with patch('random.sample', randmock):
            result = structs.sample_list_dict(self.case, 3)
            self.assertEqual(result, self.expected)


    def test_sample_list_dict_low_mem(self):
        randmock = MagicMock(return_value=[1, 2, 5])
        with patch('random.sample', randmock):
            result = structs.sample_list_dict_low_mem(self.case, 1)
            self.assertEqual(result, self.expected)


if __name__ == '__main__':
    unittest.main()
