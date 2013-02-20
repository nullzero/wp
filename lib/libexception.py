# -*- coding: utf-8  -*-
"""
Exception classes used throughout the library.
"""

import sys

try: import preload
except:
    print "E: Can't connect to library!"
    sys.exit()

import pwikipedia as pywikibot

class TableError(pywikibot.Error):
    """The table is in a invalid form."""
