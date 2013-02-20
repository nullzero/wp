# -*- coding: utf-8  -*-
"""
Exception classes used throughout the library.
"""

__version__ = "1.0.1"
__author__ = "Sorawee Porncharoenwase"

import sys
import preload
import pwikipedia as pywikibot

class TableError(pywikibot.Error):
    """The table is in a invalid form."""
