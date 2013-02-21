# -*- coding: utf-8  -*-
"""
Library to extract information from a service. Also clear the page
of service so that it is ready for next customer.
"""

__version__ = "1.0.1"
__author__ = "Sorawee Porncharoenwase"

import sys, difflib, re
import preload
import pwikipedia as pywikibot
from lib import libwikitable, libinfo

def service(serviceTitle, operation, verifyFunc, datwiki, site, summary):
    """
    Get:
        Title of service's page
        Key to read from config page,
        Function to verify user
        Config page, site
        Summary function.

    Function:
        Clear service's page

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
    histlist = []

    for version in hist:
        histlist.append((version, page.getOldVersion(version[0])))
        if version[0] == lastrev:
            break

    hist = histlist
    hist.reverse()
    for i in xrange(len(hist) - 1):
        oldv = hist[i][1]
        newv = hist[i + 1][1]
        usernew = hist[i + 1][0][2]
        dummy, cold = libwikitable.wiki2table(oldv)
        dummy, cnew = libwikitable.wiki2table(newv)
        oldvc = set([unicode(x) for x in cold])
        newvc = set([unicode(x) for x in cnew])
        difference = [eval(x) for x in (newvc - oldvc)]
        if not verifyFunc(usernew):
            for entry in difference:
                for cnt, fentry in enumerate(table):
                    if entry == fentry:
                        disable[cnt] = True
                        break

    newcontent = re.sub(ur"(?ms)^(\!.*?$\n).*?(^\|\})", ur"\1\2", oldcontent)

    if oldcontent != newcontent:
        page = pywikibot.Page(site, page.title())
        ret = page.put(newcontent, summary())
        libinfo.putdat(key=operation, value=ret[2]['newrevid'],
                        wikipage=datwiki)

    return header, table, disable
