# -*- coding: utf-8  -*-

import sys

try: import preload
except:
    print "เรียกใช้ไลบรารีไม่ได้ จบการทำงาน!"
    sys.exit()

class LimitedSortedList(object):
    def __init__(self, cmpfunc, lazy = 200000, lim = 1000):
        self.data = []
        self.cmpfunc = cmpfunc
        self.lazy = lazy
        self.lim = lim
    
    def append(self, data):
        self.data.append(data)
        self.lazyop()
    
    def concat(self, data):
        self.data += data
        self.lazyop()
    
    def lazyop(self):
        if len(self.data) > self.lazy:
            self.data.sort(cmp = self.cmpfunc)
            del self.data[self.lim:]

    def get(self):
        self.data.sort(cmp = self.cmpfunc)
        return self.data
