# -*- coding: utf-8  -*-
"""
Generator library.
"""

__version__ = "1.0.1"
__author__ = "Sorawee Porncharoenwase"

import sys
import preload
import pagegenerators

def CatGenerator(catname):
    """Quick way to get category generator."""
    return pagegenerators.GeneratorFactory().getCategoryGen(u':' + catname, 0)
