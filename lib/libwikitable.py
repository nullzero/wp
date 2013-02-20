# -*- coding: utf-8  -*-
"""
Library to convert wikitable to list of data.

Constraint:
    Can be used only when the table doesn't have any markup such as
        'rowspan', 'align' (except markup for all cells).
    The table should be a normal table; Its header should be at only the first row.
    There is no caption (|+).
    Don't support multiline cell.
    All rows must have the same length of columns.
"""

import sys, re

try: import preload
except:
    print "E: Can't connect to library!"
    sys.exit()

import pwikipedia as pywikibot
from lib import libstring, libexception
    
def wiki2table(content):
    """
    Get text. Return information in table of that text:
        Header
        List of data
    
    Known issues:
        What is the meaning of '||' at the beginning of line?
    """
    obj = re.search(ur"(?ms)(^\{\|.*?^\|\})", content)
    if not obj: raise libexception.TableError

    content = obj.group(1)
    content = libstring.repSub(ur"(?m)(^\!.*?)\!\!", u"\\1\n!", content)
    content = libstring.repSub(ur"(?m)(^\|.*?)\|\|", u"\\1\n|", content)
    header = []
    lines = content.split(u"\n")
    
    for line in lines:
        if line.startswith(u"!"):
            header.append(line[1:].strip())
    
    table = []
    linelist = []
    
    for line in lines:
        if line.startswith(u"|-") or line.startswith(u"|}"):
            if linelist:
                table.append(linelist)
                linelist = []
        elif line.startswith(u"|"):
            linelist.append(line[1:].strip())
    
    for line in table:
        if len(line) != len(header): raise libexception.TableError
    
    header = (re.search(ur"(?m)^\{\|.*?$", content).group(), header)
    return header, table
