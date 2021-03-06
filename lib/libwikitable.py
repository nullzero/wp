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

__version__ = "1.0.1"
__author__ = "Sorawee Porncharoenwase"

import sys
import preload
import pwikipedia as pywikibot
from lib import re2, libexception
    
def wiki2table(content):
    """
    Get text. Return information in table of that text:
        Header
        List of data
    
    Known issues:
        What is the meaning of '||' at the beginning of line?
    """
    try:
        content = re2.find(ur"(?ms)^\{\|.*?^\|\}", content)
    except AttributeError:
        raise libexception.TableError

    content = re2.subr(ur"(?m)(^\!.*?)\!\!", u"\\1\n!", content)
    content = re2.subr(ur"(?m)(^\|.*?)\|\|", u"\\1\n|", content)
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
        if len(line) != len(header):
            raise libexception.TableError
    
    header = (re2.find(ur"(?m)^\{\|.*?$", content), header)
    return header, table
