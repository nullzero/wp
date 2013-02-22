# -*- coding: utf-8  -*-
"""
Library to manipulate string
"""

__version__ = "1.0.1"
__author__ = "Sorawee Porncharoenwase"

import re, sys

def toCompile(pattern):
    if isinstance(pattern, basestring):
        return re.compile(pattern)
    return pattern

def findOverlap(pattern, text):
    """Find all patterns in given text overlappingly."""
    return sum([1 for x in toCompile(u"(?=(%s))" % 
                                    pattern).finditer(text) if x])

def repSub(pattern, replacetext, text):
    """Substitute by regex until there is no change."""
    pattern = toCompile(pattern)
    while True:
        oldtext = text
        text = pattern.sub(replacetext, text)
        if text == oldtext:
            break
    return text
