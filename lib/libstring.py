# -*- coding: utf-8  -*-

import re, sys

try: import preload
except:
    print "เรียกใช้ไลบรารีไม่ได้ จบการทำงาน!"
    sys.exit()

def findOverlap(pattern, text):
    pat = u"(?=(%s))" % pattern
    it = re.finditer(pat, text)
    cnt = 0
    for i in it: cnt += 1
    return cnt

def repSub(pattern, replacetext, text):
    while True:
        oldtext = text
        text = re.sub(pattern, replacetext, text)
        if text == oldtext: break
    return text
