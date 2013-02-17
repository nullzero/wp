# -*- coding: utf-8  -*-

import sys, os, traceback, datetime, inspect

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../patch")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../pywikipedia")))

try: import wikipedia as pywikibot
except:
    print traceback.format_exc()
    sys.exit()

def error(): pywikibot.output(traceback.format_exc().decode("utf-8"))
def getTime(): return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

summarySuffix = u" หากผิดพลาดโปรดแจ้ง[[User talk:Nullzero|ที่นี่]]"

global_name = None
global_lockfile = None

def pre(name, lock = False):
    pywikibot.handleArgs("-log")
    global global_name, global_lockfile
    global_name = name
    pywikibot.output(u"สคริปต์" + global_name + u"เริ่มทำงานในเวลา " + getTime())
    if lock:
        global_lockfile = os.path.join("/tmp", os.path.basename(sys.argv[0]) + ".wp.lock")
        if os.path.exists(global_lockfile):
            pywikibot.output(u"!!! มีการล็อกอยู่อยู่")
            pywikibot.stopme()
            sys.exit()
        open(global_lockfile, 'w').close()
    return pywikibot.handleArgs(), pywikibot.getSite()

def post(unlock = True):
    if unlock and global_lockfile:
        try: os.remove(global_lockfile)
        except: pywikibot.output(u"!!! ลบไฟล์ล็อกไม่ได้")
    pywikibot.output(u"สคริปต์" + global_name + u"หยุดทำงานในเวลา " + getTime())
    pywikibot.stopme()
    sys.exit()

def posterror():
    error()
    pywikibot.output(u"!!! จบการทำงานทันที")
    post(unlock = False)

"""
def simplifyPath(path):
    return os.path.abspath(os.path.expanduser(path))

def File(path, name):
    return os.path.join(os.path.dirname(path), name)
"""
