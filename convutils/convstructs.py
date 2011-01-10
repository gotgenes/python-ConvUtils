#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
A collection of convenient Python data structures.

"""

__author__ = 'Chris Lasher'
__email__ = 'chris DOT lasher <AT> gmail DOT com'


import collections


class SortedTupleKeysDict(dict):
    """A dictionary that always sorts the items in its tuple keys."""

    def __contains__(self, key):
        key = tuple(sorted(key))
        return super(SortedTupleKeysDict, self).__contains__(key)


    def __delitem__(self, key):
        key = tuple(sorted(key))
        return super(SortedTupleKeysDict, self).__delitem__(key)


    def __getitem__(self, key):
        key = tuple(sorted(key))
        return super(SortedTupleKeysDict, self).__getitem__(key)


    def __setitem__(self, key, value):
        key = tuple(sorted(key))
        super(SortedTupleKeysDict, self).__setitem__(key, value)


    def has_key(self, key):
        key = tuple(sorted(key))
        return super(SortedTupleKeysDict, self).has_key(key)


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

        Returns `True` if the item is among the values, or `False` if
        the item is not.

        :Parameters:
        - `item`: an item that may be among the `set`s in the
          main dictionary's values

        """
        if item in self._reverse_dict:
            return True
        else:
            return False


    def item_has_key(self, item, key):
        """See if an item in the values of the dictionary has a reverse
        mapping to an item.

        Raises a `KeyError` if the item is not present in any of the
        values.

        Returns True if the item has a reverse mapping to the key, or
        False if the item has no reverse mapping to the key.

        :Parameters:
        - `item`: an item in one of the value sets
        - `key`: a key of the dictionary

        """
        if key in self._reverse_dict[item]:
            return True
        else:
            return False


    def get_item_keys(self, item):
        """Returns a `set` of all keys whose `set` values the item is
        present in.

        Raises a `KeyError` if the item is not present in any of the
        values.

        :Parameters:
        - `item`: an item in one of the value sets

        """
        return self._reverse_dict[item]


    def add_item(self, key, item):
        """Adds a item to the set belonging to the key.

        Raises a `KeyError` if the key does not exist.

        :Parameters:
        - `key`: a key in the main dictionary
        - `item`: an item to be added to the set belonging to the key

        """
        self[key].add(item)
        try:
            self._reverse_dict[item].add(key)
        except KeyError:
            self._reverse_dict[item] = set([key])


    def remove_item(self, key, item):
        """Removes an item from the set belonging to the key.

        Raises a `KeyError` if the key does not exist, or if the item
        is not present in the set belonging to the key.

        :Parameters:
        - `key`: a key in the main dictionary
        - `item`: an item to be removed from the set belonging to the
          key

        """
        self[key].remove(item)
        self._remove_reverse_mapping(item, key)


    def remove_item_from_all_keys(self, item):
        """Removes an item from all `set` values in the main dictionary
        to which it belongs.

        Raises a `KeyError` if the item is not present in any of the
        values.

        :Parameters:
        - `item`: an item to be removed from all sets of values

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

