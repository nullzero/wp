# -*- coding: utf-8  -*-
"""
Library to manipulate string
"""

__version__ = "1.0.1"
__author__ = "Sorawee Porncharoenwase"

import re, sys

def findOverlap(pattern, text):
    """Find all patterns in given text overlappingly."""
    pat = u"(?=(%s))" % pattern
    it = re.finditer(pat, text)
    cnt = 0
    for i in it:
        cnt += 1
    return cnt

def repSub(pattern, replacetext, text):
    """Substitute by regex until there is no change."""
    while True:
        oldtext = text
        text = re.sub(pattern, replacetext, text)
        if text == oldtext:
            break
    return text
