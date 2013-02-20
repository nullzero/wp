# -*- coding: utf-8  -*-
"""
Data structures library.
"""

__version__ = "1.0.1"
__author__ = "Sorawee Porncharoenwase"

import sys
import preload

class LimitedSortedList(object):
    """
    A data structure to store sorted data. Since only few elements at
    the beginning of the list are required, Amortized algorithm can
    help speeding up the operations.
    """
    def __init__(self, cmpfunc, lazy = 200000, lim = 1000):
        """
        Get:
            cmpfunc(a, b):  if return value is negative, then a < b,
                            else, a >= b.
            lazy:           a number of operations that will trigger
                            lazy operation.
            lim:            length of required data.
        """
        self.data = []
        self.cmpfunc = cmpfunc
        self.lazy = lazy
        self.lim = lim
    
    def append(self, data):
        """Append an element to list."""
        self.data.append(data)
        self.__lazyop()
    
    def concat(self, data):
        """Concatenate list with list."""
        self.data += data
        self.__lazyop()
    
    def __lazyop(self):
        """Lazy operation."""
        if len(self.data) > self.lazy:
            self.data.sort(cmp = self.cmpfunc)
            del self.data[self.lim:]

    def get(self):
        """Return top 'lim' elements"""
        self.data.sort(cmp = self.cmpfunc)
        return self.data
