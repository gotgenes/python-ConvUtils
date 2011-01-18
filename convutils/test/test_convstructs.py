#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2011 Christopher D. Lasher
#
# This software is released under the MIT License. Please see
# LICENSE.txt for details.


"""Tests for convstructs.py"""

__author__ = 'Chris Lasher'
__email__ = 'chris DOT lasher <AT> gmail DOT com'


import unittest

import os
import sys

parpath = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(parpath))

import convstructs


class TwoWaySetDictTests(unittest.TestCase):

    def setize_kv_pairs(self, kv_pairs):
        """Helper function to turn `sets` in the values of dictionary
        key-value pairs (items) into `frozenset`s.

        Returns a `set` of key-value pairs with values as `frozenset`s.

        :Parameters:
        - `kv_pairs`: the key-value pairs from `dict.items()`

        """
        frozen_kv_pairs = ((k, frozenset(v)) for (k, v) in kv_pairs)
        setized_kv_pairs = set(frozen_kv_pairs)
        return setized_kv_pairs


    def check_items_and_reverse_dict(
            self,
            two_way_dict,
            expected_items,
            expected_reverse_dict
        ):
        """Check the internals of the two-way dictionary.

        :Parameters:
        - `two_way_dict`: a `TwoWaySetDict` instance
        - `expected_items`: a `set` of the expected key-value pairs
        - `expected_reverse_dict`: a dictionary of what's expected for
          the `TwoWaySetDict._reverse_dict`

        """
        items = self.setize_kv_pairs(two_way_dict.items())
        self.assertEqual(items, expected_items)
        self.assertEqual(
                two_way_dict._reverse_dict,
                expected_reverse_dict
        )


    def setUp(self):
        self.two_way_dict = convstructs.TwoWaySetDict()


    def test_init_empty(self):
        two_way_dict = convstructs.TwoWaySetDict()
        expected_items = set()
        expected_reverse_dict = {}
        self.check_items_and_reverse_dict(
                two_way_dict,
                expected_items,
                expected_reverse_dict
        )


    def test_init_bad_arg(self):
        """Check __init__ raises error if `arg` has a value that's not a
        set.

        """
        self.assertRaises(
                ValueError,
                convstructs.TwoWaySetDict,
                [('a', set([1])), ('b', 2)]
        )


    def test_init_bad_kwargs(self):
        """Check __init__ raises error if **kwargs has a value that's
        not a set.

        """
        try:
            convstructs.TwoWaySetDict(a=set([1]), b=2)
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError not raised")


    def test_init_with_arg(self):
        two_way_dict = convstructs.TwoWaySetDict(
                [('a', set([1])), ('b', set([1, 2]))]
        )
        expected_items = set([
                ('a', frozenset([1])),
                ('b', frozenset([1, 2]))
        ])
        expected_reverse_dict = {1: set(['a', 'b']), 2: set(['b'])}
        self.check_items_and_reverse_dict(
                two_way_dict,
                expected_items,
                expected_reverse_dict
        )


    def test_init_with_kwargs(self):
        two_way_dict = convstructs.TwoWaySetDict(
                a=set([1]),
                b=set([1, 2])
        )
        expected_items = set([
                ('a', frozenset([1])),
                ('b', frozenset([1, 2]))
        ])
        expected_reverse_dict = {1: set(['a', 'b']), 2: set(['b'])}
        self.check_items_and_reverse_dict(
                two_way_dict,
                expected_items,
                expected_reverse_dict
        )


    def test_init_with_arg_and_kwargs(self):
        two_way_dict = convstructs.TwoWaySetDict(
                [('a', set([3]))],
                a=set([1]),
                b=set([1, 2])
        )
        expected_items = set([
                ('a', frozenset([1])),
                ('b', frozenset([1, 2]))
        ])
        expected_reverse_dict = {1: set(['a', 'b']), 2: set(['b'])}
        self.check_items_and_reverse_dict(
                two_way_dict,
                expected_items,
                expected_reverse_dict
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
        expected_reverse_dict = {1 : set('a')}
        self.check_items_and_reverse_dict(
                self.two_way_dict,
                expected_items,
                expected_reverse_dict
        )


    def test_reassign_entry(self):
        self.two_way_dict['a'] = set([1, 2])
        self.two_way_dict['a'] = set([2, 3])
        expected_items = set([('a', frozenset([2, 3]))])
        expected_reverse_dict = {2: set('a'), 3: set('a')}
        self.check_items_and_reverse_dict(
                self.two_way_dict,
                expected_items,
                expected_reverse_dict
        )


    def test_insert_multiple_entries_uncommon_value(self):
        self.two_way_dict['a'] = set([1])
        self.two_way_dict['b'] = set([2])
        expected_items = set([
                ('a', frozenset([1])),
                ('b', frozenset([2]))
        ])
        expected_reverse_dict = {1: set(['a']), 2: set(['b'])}
        self.check_items_and_reverse_dict(
                self.two_way_dict,
                expected_items,
                expected_reverse_dict
        )


    def test_insert_multiple_entries_common_value(self):
        self.two_way_dict['a'] = set([1])
        self.two_way_dict['b'] = set([1])
        expected_items = set([
                ('a', frozenset([1])),
                ('b', frozenset([1]))
        ])
        expected_reverse_dict = {1: set(['a', 'b'])}
        self.check_items_and_reverse_dict(
                self.two_way_dict,
                expected_items,
                expected_reverse_dict
        )


    def test_insert_entry_multiple_values(self):
        self.two_way_dict['a'] = set([1, 2])
        expected_items = set([('a', frozenset([1, 2]))])
        expected_reverse_dict = {1: set(['a']), 2: set(['a'])}
        self.check_items_and_reverse_dict(
                self.two_way_dict,
                expected_items,
                expected_reverse_dict
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
        expected_reverse_dict = {}
        self.check_items_and_reverse_dict(
                self.two_way_dict,
                expected_items,
                expected_reverse_dict
        )


    def test_del_one_key(self):
        self.two_way_dict['a'] = set([1, 2])
        del self.two_way_dict['a']
        expected_items = set()
        expected_reverse_dict = {}
        self.check_items_and_reverse_dict(
                self.two_way_dict,
                expected_items,
                expected_reverse_dict
        )


    def test_del_multiple_keys(self):
        self.two_way_dict['a'] = set([1, 2])
        self.two_way_dict['b'] = set([2])
        del self.two_way_dict['a']
        expected_items = set([('b', frozenset([2]))])
        expected_reverse_dict = {2: set(['b'])}
        self.check_items_and_reverse_dict(
                self.two_way_dict,
                expected_items,
                expected_reverse_dict
        )


    def test_copy(self):
        self.two_way_dict['a'] = set([1, 2])
        self.two_way_dict['b'] = set([1])
        twd_copy = self.two_way_dict.copy()
        expected_items = set([
                ('a', frozenset([1, 2])),
                ('b', frozenset([1]))
        ])
        expected_reverse_dict = {1: set(['a', 'b']), 2: set(['a'])}
        self.check_items_and_reverse_dict(
                twd_copy,
                expected_items,
                expected_reverse_dict
        )


    def test_clear(self):
        self.two_way_dict['a'] = set([1, 2])
        self.two_way_dict['b'] = set([1])
        self.two_way_dict.clear()
        expected_items = set()
        expected_reverse_dict = {}
        self.check_items_and_reverse_dict(
                self.two_way_dict,
                expected_items,
                expected_reverse_dict
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
        expected_reverse_dict = {1: set(['a'])}
        self.check_items_and_reverse_dict(
                self.two_way_dict,
                expected_items,
                expected_reverse_dict
        )


    def test_add_item_single_key(self):
        self.two_way_dict['a'] = set([1])
        self.two_way_dict.add_item('a', 2)
        expected_items = set([('a', frozenset([1, 2]))])
        expected_reverse_dict = {1: set(['a']), 2: set(['a'])}
        self.check_items_and_reverse_dict(
                self.two_way_dict,
                expected_items,
                expected_reverse_dict
        )


    def test_add_item_multiple_keys(self):
        self.two_way_dict['a'] = set([1])
        self.two_way_dict['b'] = set([2])
        self.two_way_dict.add_item('a', 2)
        expected_items = set([
                ('a', frozenset([1, 2])),
                ('b', frozenset([2]))
        ])
        expected_reverse_dict = {1: set(['a']), 2: set(['a', 'b'])}
        self.check_items_and_reverse_dict(
                self.two_way_dict,
                expected_items,
                expected_reverse_dict
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
        expected_reverse_dict = {}
        self.check_items_and_reverse_dict(
                self.two_way_dict,
                expected_items,
                expected_reverse_dict
        )


    def test_remove_item_multiple_keys(self):
        self.two_way_dict['a'] = set([1])
        self.two_way_dict['b'] = set([1])
        self.two_way_dict.remove_item('a', 1)
        expected_items = set([
                ('a', frozenset()),
                ('b', frozenset([1]))
        ])
        expected_reverse_dict = {1: set(['b'])}


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
        expected_reverse_dict = {2: set(['b'])}



if __name__ == '__main__':
    unittest.main()
