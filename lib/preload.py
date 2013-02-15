# -*- coding: utf-8  -*-

import sys, os, traceback, datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../patch")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../pywikipedia")))

try: import wikipedia as pywikibot
except:
    print traceback.format_exc()
    sys.exit()

def error(): pywikibot.output(traceback.format_exc().decode("utf-8"))
def getTime(): return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

site = pywikibot.getSite()

summarySuffix = u" หากผิดพลาดโปรดแจ้ง[[User talk:Nullzero|ที่นี่]]"

"""
def simplifyPath(path):
    return os.path.abspath(os.path.expanduser(path))

def File(path, name):
    return os.path.join(os.path.dirname(path), name)
"""
