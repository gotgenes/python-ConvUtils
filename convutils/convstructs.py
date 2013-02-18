#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2011, 2013 Christopher D. Lasher
#
# This software is released under the MIT License. Please see
# LICENSE.txt for details.


"""A collection of convenient Python data structures."""

from __future__ import absolute_import

import bisect
from collections import defaultdict, MutableMapping
import random

from convutils.convutils import cumsum


class SortedTupleKeysDict(MutableMapping):
    """A dictionary that always sorts the items in its tuple keys."""

    def __init__(self, items=None, **kwargs):
        if items is not None:
            items = [(self.__keytransform__(item[0]), item[1]) for item
                         in items]
        kwargs = dict((self.__keytransform__(item[0]), item[1]) for item
                      in kwargs.iteritems())
        self._store = dict(items, **kwargs)


    def __keytransform__(self, key):
        return tuple(sorted(key))


    def __contains__(self, key):
        return self.__keytransform__(key) in self._store


    def __getitem__(self, key):
        return self._store[self.__keytransform__(key)]


    def __setitem__(self, key, value):
        self._store[self.__keytransform__(key)] = value


    def __delitem__(self, key):
        del self._store[self.__keytransform__(key)]


    def __iter__(self):
        return iter(self._store)


    def __len__(self):
        return len(self._store)


class TwoWaySetDict(dict):
    """A dictionary that has sets as values, and allows looking up the
    key of any item that is in at least one set within the values.

    """

    def __init__(self, arg=None, **kwargs):
        if arg is None:
            arg = []
        super(TwoWaySetDict, self).__init__(arg, **kwargs)

        self._reverse_dict = {}
        for key, value in self.iteritems():
            if not isinstance(value, set):
                raise ValueError("Value %(value)s is not an instance "
                        "of set in pair (%(key)s, %(value)s)" %
                        {'key': key, 'value': value}
                )
            for item in value:
                try:
                    self._reverse_dict[item].add(key)
                except KeyError:
                    self._reverse_dict[item] = set([key])


    def __setitem__(self, key, value):
        if not isinstance(value, set):
            raise ValueError("value should be an instance of set")

        if key in self:
            # remove the old reverse mappings
            for item in self[key]:
                if item not in value:
                    self._remove_reverse_mapping(item, key)

        for item in value:
            try:
                self._reverse_dict[item].add(key)
            except KeyError:
                self._reverse_dict[item] = set([key])
        super(TwoWaySetDict, self).__setitem__(key, value)


    def __delitem__(self, key):
        value = self[key]
        for item in value:
            self._remove_reverse_mapping(item, key)
        super(TwoWaySetDict, self).__delitem__(key)


    def _remove_reverse_mapping(self, reverse_key, key):
        """Removes the reverse key to key mapping from the reverse
        dictionary, removing the reverse key from the reverse dictionary
        if it no longer maps to any keys.

        """
        self._reverse_dict[reverse_key].remove(key)
        if not self._reverse_dict[reverse_key]:
            del self._reverse_dict[reverse_key]


    def copy(self):
        """Return a shallow copy."""
        return self.__class__(self)


    def clear(self):
        self._reverse_dict.clear()
        super(TwoWaySetDict, self).clear()


    def reverse_keys(self):
        """Returns a list of the keys of the reverse dictionary.

        These items are the items in the value sets of the main
        dictionary.

        """
        return self._reverse_dict.keys()


    def reverse_iterkeys(self):
        """Returns an iterable of the keys of the reverse dictionary.

        These items are the items in the value sets of the main
        dictionary.

        """
        return self._reverse_dict.iterkeys()


    def reverse_values(self):
        """Returns a list of the values of the reverse dictionary.

        These values are sets of the keys in the main dictionary.

        """
        return self._reverse_dict.values()


    def reverse_itervalues(self):
        """Returns an iterable of the values of the reverse dictionary.

        These values are sets of the keys in the main dictionary.

        """
        return self._reverse_dict.itervalues()


    def reverse_items(self):
        """Returns a list of tuples for reverse key and value pairs.

        """
        return self._reverse_dict.items()


    def reverse_iteritems(self):
        """Yields individual key-value pairs for the reversed items.

        """
        return self._reverse_dict.iteritems()


    def has_item(self, item):
        """Performs a reverse-lookup to see if an item exists among the
        sets in the dictionary's values.

        Returns ``True`` if the item is among the values, or ``False``
        if the item is not.

        :param item: an item that may be among the ``set``s in the
          main dictionary's values

        """
        if item in self._reverse_dict:
            return True
        else:
            return False


    def item_has_key(self, item, key):
        """See if an item in the values of the dictionary has a reverse
        mapping to an item.

        Raises a ``KeyError`` if the item is not present in any of the
        values.

        Returns True if the item has a reverse mapping to the key, or
        False if the item has no reverse mapping to the key.

        :param item: an item in one of the value sets
        :param key: a key of the dictionary

        """
        if key in self._reverse_dict[item]:
            return True
        else:
            return False


    def get_item_keys(self, item):
        """Returns a ``set`` of all keys whose ``set`` values the item
        is present in.

        Raises a ``KeyError`` if the item is not present in any of the
        values.

        :param item: an item in one of the value sets

        """
        return self._reverse_dict[item]


    def add_item(self, key, item):
        """Adds a item to the set belonging to the key.

        Raises a ``KeyError`` if the key does not exist.

        :param key: a key in the main dictionary
        :param item: an item to be added to the set belonging to the key

        """
        self[key].add(item)
        try:
            self._reverse_dict[item].add(key)
        except KeyError:
            self._reverse_dict[item] = set([key])


    def remove_item(self, key, item):
        """Removes an item from the set belonging to the key.

        Raises a ``KeyError`` if the key does not exist, or if the item
        is not present in the set belonging to the key.

        :param key: a key in the main dictionary
        :param item: an item to be removed from the set belonging to the
          key

        """
        self[key].remove(item)
        self._remove_reverse_mapping(item, key)


    def remove_item_from_all_keys(self, item):
        """Removes an item from all ``set`` values in the main
        dictionary to which it belongs.

        Raises a ``KeyError`` if the item is not present in any of the
        values.

        :param item: an item to be removed from all sets of values

        """
        for key in self._reverse_dict[item]:
            self[key].remove(item)
        del self._reverse_dict[item]


    # TODO: implement the following
    #def pop(self):
    #def popitem(self):
    #def reverse_pop(self):
    #def reverse_popitem(self):
    #def update(self, *other):


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
    sampled_d = defaultdict(list)
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
    sampled_d = defaultdict(list)
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

