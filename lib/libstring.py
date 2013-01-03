# -*- coding: utf-8  -*-

import re, sys

try: import preload
except:
    print "Cannot import preload. Exit!"
    sys.exit()

def findOverlap(pattern, text):
    pat = u"(?=(%s))" % pattern
    it = re.finditer(pat, text)
    cnt = 0
    for i in it: cnt += 1
    return cnt
