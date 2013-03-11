# -*- coding: utf-8  -*-
"""
Library to set basic environment. It also provide frequently used
function. This library should be imported in every script that require
to connect to pywikipedia library
"""

__version__ = "1.0.1"
__author__ = "Sorawee Porncharoenwase"

import sys, os, traceback, datetime, imp

def File(path, name):
    return os.path.abspath(os.path.join(os.path.dirname(path), name))

sys.path.append(File(__file__, ".."))
sys.path.append(File(__file__, "../patch"))
sys.path.append(File(__file__, "../pywikipedia"))

import wikipedia as pywikibot
from conf import glob as conf

def deunicode(st):
    """Return normal quoted string."""
    try:
        st = str(st)
    except UnicodeEncodeError:
        st = st.encode("utf-8")
    return st

def enunicode(st):
    """Return unicode quoted string."""
    try:
        st = unicode(st)
    except UnicodeDecodeError:
        st = st.decode("utf-8")
    return st

def error(e=None):
    """
    If error message is given, print that error message. Otherwise,
    print traceback instead.
    """
    if e:
        pywikibot.output(u"E: " + e)
    else:
        exc = sys.exc_info()[0]
        if (exc == KeyboardInterrupt) or (exc == SystemExit):
            sys.exit()
        pywikibot.output(u"E: " + enunicode(traceback.format_exc()))

def getTime():
    """Print timestamp."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

fullname = None
lockfile = None
basescript = os.path.basename(sys.argv[0])
dirname = os.path.dirname(sys.argv[0])

def pre(name, lock = False):
    """
    Return argument list, site object, and configuration of the script.
    This function also handles default arguments, generates lockfile
    and halt the script if lockfile exists before.
    """
    global fullname, lockfile
    pywikibot.handleArgs("-log")
    fullname = name
    pywikibot.output(u"The script " + fullname + u". Start at " + getTime())
    if lock:
        lockfile = os.path.abspath("../../tmp/" + basescript + ".py")
        if os.path.exists(lockfile):
            error(u"Lockfile found. Unable to execute the script.")
            pywikibot.stopme()
            sys.exit()
        open(lockfile, 'w').close()

    confpath = os.path.abspath("../../conf/" + basescript + ".py")
    if os.path.exists(confpath):
        module = imp.load_source("conf", confpath)
    else:
        module = None
    return pywikibot.handleArgs(), pywikibot.getSite(), module

def post(unlock = True):
    """
    This function removes throttle file. It also removes lockfile unless
    unlock variable is set to False
    """
    if unlock and lockfile:
        try:
            os.remove(lockfile)
        except OSError:
            error(u"Unable to remove lockfile.")

    pywikibot.output(u"The script " + fullname + u". Stop at " + getTime())
    pywikibot.stopme()
    sys.exit()

def posterror():
    """This function forces program stop without removing lockfile"""
    error()
    error(u"Suddenly halt!")
    post(unlock = False)
