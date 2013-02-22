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
        return self.regex.search(text).group(group)
    
    def findall(self, text):
        return self.regex.findall(text)
    
    def finditer(self, text):
        return self.regex.finditer(text)
    
    def sub(self, subst, text):
        return self.regex.sub(subst, text)

patWikilink = re2(ur"(?<=\[\[).*?(?=\]\])")

def find(pat, text, group=0):
    return re2(pat).find(text, group)

def search(pat, text):
    return re2(pat).search()

def findall(pat, text):
    return re2(pat).findall(text)

def finditer(pat, text):
    return re2(pat).finditer(text)
    
def sub(pat, subst, text):
    return re2(pat).sub(subt, text)

""" More function! """
def genData(tagind, tag):
    return re2(u"(?s)(?<=<!-- %s%s -->).*?(?=<!-- %s%s -->)" %
                        (tagind[0], tag, tagind[1], tag))

def genSep(l):
    return re2(u"|".join(l))

def getconf(key, text):
    return re2(u"(?<=<!-- %s \{).*?(?=\} -->)" % key).find(text)
