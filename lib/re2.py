# -*- coding: utf-8  -*-
"""
Provide some frequently used regex.
"""

__version__ = "1.0.1"
__author__ = "Sorawee Porncharoenwase"

import re

class re2(object):
    def __init__(self, pat):
        self.regex = re.compile(pat)
        
    def search(self, text):
        return self.regex.search(text)
        
    def find(self, text, group=0):
        _x = self.regex.search(text)
        if _x:
            return _x.group(group)
        else:
            return None
    
    def findall(self, text):
        return self.regex.findall(text)
    
    def finditer(self, text):
        return self.regex.finditer(text)
    
    def sub(self, subst, text):
        return self.regex.sub(subst, text)
    
    def subn(self, subst, text):
        return self.regex.subn(subst, text)
    
    def subr(self, subst, text):
        """Substitute by regex until there is no change."""
        while True:
            oldtext = text
            text = self.regex.sub(subst, text)
            if text == oldtext:
                break
        return text
    
    @property
    def pattern(self):
        return self.regex.pattern
        
class subst(object):
    def __init__(self):
        self._all = []
        
    def append(self, p):
        self._all.append((re2(p[0]), p[1]))
    
    def do(self, s, rep=False):
        if not isinstance(s, basestring):
            s = s.group()
        if rep:
            func = lambda _x, _y: _x[0].subr(_x[1], _y)
        else:
            func = lambda _x, _y: _x[0].sub(_x[1], _y)
            
        for i in self._all:
            s = func(i, s)
        return s

def find(pat, text, group=0):
    return re2(pat).find(text, group)

def search(pat, text):
    return re2(pat).search(text)

def findall(pat, text):
    return re2(pat).findall(text)

def finditer(pat, text):
    return re2(pat).finditer(text)
    
def sub(pat, subst, text):
    return re2(pat).sub(subst, text)

def subn(pat, subst, text):
    return re2(pat).subn(subst, text)

def subr(pat, subst, text):
    return re2(pat).subr(subst, text)

def escape(s):
    return re.escape(s)

""" More functions! """
def genData(tagind, tag):
    return re2(u"(?s)(?<=<!-- %s%s -->).*?(?=<!-- %s%s -->)" %
                        (tagind[0], tag, tagind[1], tag))

def sep(l):
    return u"(?:" + u"|".join(l) + u")"

def getconf(key, text):
    return re2(u"(?<=<!-- %s \{).*?(?=\} -->)" % key).find(text)

def findOverlap(pattern, text):
    """Find all patterns in given text overlappingly."""
    return sum([1 for x in finditer(u"(?=(" + pattern + u"))", text) if x])

""" More patterns! """
patWikilink = re2(ur"(?<=\[\[).*?(?=\]\])")
