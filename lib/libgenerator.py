# -*- coding: utf-8  -*-
"""
Generator library.
"""

__version__ = "1.0.1"
__author__ = "Sorawee Porncharoenwase"

import sys, itertools
import preload
import pwikipedia as pywikibot
import pagegenerators, catlib
from lib import re2

def glob():
    global patTrimCat
    patTrimCat = re2.re2(ur".*\:")

def CatGenerator(cat, site=None, subcat=False, recurse=False):
    """Quick way to get category generator."""
    if site is None:
        site = pywikibot.getSite()
    if isinstance(cat, pywikibot.Page):
        site = cat.site()
        cat = cat.title()
    return itertools.chain(
            pagegenerators.CategorizedPageGenerator(catlib.Category(site, cat),
                                                    recurse=recurse),
            pagegenerators.SubCategoriesPageGenerator(catlib.Category(site, cat),
                                                    recurse=recurse)
                if subcat else [])

glob()
