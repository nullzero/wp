# -*- coding: utf-8  -*-
"""
Library to manage everything related to stroing information.
I/O can be file or wiki page.
"""

__version__ = "1.0.1"
__author__ = "Sorawee Porncharoenwase"

import sys, os, re
import preload

def extract(key, text):
    """
    Extract key from text. Note that both key and text must be unicode
    strings.
    """
    if key:
        try:
            dat = unicode(re.search(u"(?m)^\* " + re.escape(key) + u": (.*?)$",
                                    text).group(1))
        except AttributeError:
            dat = None
    else:
        lines = text.strip().split(u"\n")
        dat = {}
        for line in lines:
            key, value = line.split(u": ")
            dat[key] = value
            
    return dat

def changeValue(key, value, text):
    """
    Return text which value of given key is changed.
    """
    text = text.strip()
    text, changes = re.subn(u"(?m)^\* %s: (.*?)$" % re.escape(key),
                            u"* %s: %s" % (re.escape(key), value),
                            text)
    # don't check that newtext is equal to oldtext because if newvalue is 
    # equal oldvalue, it will duplicate that key.
    if changes == 0:
        if text:
            text = text + u"\n* " + key + u": " + value
        else:
            text = u"* " + key + u": " + value
    
    return text

def getdat(key = None, filename = None, wikipage = None):
    """
    Return value of given key, but if key is not given, return dict instead.
    This function will look at file first, but if file doesn't exist,
    it will look at wiki page later.
    """
    key = unicode(key)
    if filename:
        fullfilename = os.path.join(preload.dirname, filename + ".cfg")
        if os.path.exists(fullfilename):
            with open(fullfilename, "r") as f:
                text = unicode(f.read())
            
            xdata = extract(key, text)
            if xdata: return xdata
    
    if wikipage and wikipage.exists():
        return extract(key, wikipage.get())

def putdat(key, value, filename = None, wikipage = None):
    """
    Save value of given key. Saving will be operated with any I/O methods
    which are given
    """
    key = unicode(key)
    value = unicode(value)
    
    if filename:
        fullfilename = os.path.join(preload.dirname, filename + ".cfg")
        text = u""
        try:
            with open(fullfilename, "r") as f:
                text = unicode(f.read())
        except IOError:
            pass
            
        with open(fullfilename, "w") as f:
            f.write(preload.deunicode(changeValue(key, value, text)))

    if wikipage:
        wikipage.put(changeValue(key, value, wikipage.get()))
