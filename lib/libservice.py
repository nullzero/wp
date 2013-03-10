# -*- coding: utf-8  -*-
"""
Library to extract information from a service. Also clear the page
of service so that it is ready for next customer.
"""

__version__ = "1.0.1"
__author__ = "Sorawee Porncharoenwase"

import sys, difflib
import preload
import pwikipedia as pywikibot
from lib import libwikitable, libinfo, re2

def service(serviceTitle, operation, verifyFunc, datwiki, site, summary, 
            debug=False):
    """
    Get:
        Title of service"s page
        Key to read from config page,
        Function to verify user
        Config page, site
        Summary function.

    Function:
        Clear service"s page

    Return:
        Header of table
        List of rows
        Suspicious entry(/row)
    """
    page = pywikibot.Page(site, serviceTitle)
    datwiki = pywikibot.Page(site, datwiki)
    lastrev = int(libinfo.getdat(key = operation, wikipage = datwiki))
    oldcontent = page.get()
    header, table = libwikitable.wiki2table(oldcontent)
    disable = [False] * len(table)
    hist = page.getVersionHistory()
    # There is no need to get all revisions, just 500 is fine (by default).
    histlist = []

    for version in hist:
        histlist.append((version, page.getOldVersion(version[0])))
        if version[0] == lastrev:
            break
    hist = histlist
    hist.reverse()
    pywikibot.output(u"Processing %d revision(s)" % len(hist))
    for i in xrange(len(hist) - 1):
        oldv = hist[i][1]
        newv = hist[i + 1][1]
        usernew = hist[i + 1][0][2]
        dummy, cold = libwikitable.wiki2table(oldv)
        dummy, cnew = libwikitable.wiki2table(newv)
        oldvc = set([preload.enunicode(x) for x in cold])
        newvc = set([preload.enunicode(x) for x in cnew])
        difference = [eval(x) for x in (newvc - oldvc)]
        if not verifyFunc(usernew):
            for entry in difference:
                for cnt, fentry in enumerate(table):
                    if entry == fentry:
                        disable[cnt] = True
                        break

    newcontent = re2.sub(ur"(?ms)^(\!.*?$\n).*?(^\|\})", ur"\1\2", oldcontent)

    if oldcontent != newcontent:
        if not debug:
            page = pywikibot.Page(site, page.title())
            page.put(newcontent, summary())
        
        print page.getVersionHistory()[0][0]
        libinfo.putdat(key=operation, 
                        value=page.getVersionHistory()[0][0], 
                        wikipage=datwiki)
                        
    return header, table, disable
