# -*- coding: utf-8  -*-

import sys, difflib, re

try: import preload
except:
    print "เรียกใช้ไลบรารีไม่ได้ จบการทำงาน!"
    sys.exit()

import pwikipedia as pywikibot
from lib import libwikitable, libfile

def calc(page, tag, operation, verifyFunc):
    header, table = libwikitable.wiki2table(page.get(), tag)
    disable = [False] * len(table)
    hist = page.getVersionHistory()
    histlist = []
    
    lastRev = int(libfile.get("lastrev", operation))
    
    for version in hist:
        histlist.append((version, page.getOldVersion(version[0])))
        if version[0] == lastRev: break
    
    hist = histlist
    hist.reverse()
    for i in xrange(len(hist) - 1):
        oldv = hist[i][1]
        newv = hist[i + 1][1]
        usernew = hist[i + 1][0][2]
        dummy, cold = libwikitable.wiki2table(oldv, tag)
        dummy, cnew = libwikitable.wiki2table(newv, tag)
        oldvc = set([unicode(x) for x in cold])
        newvc = set([unicode(x) for x in cnew])
        difference = [eval(x) for x in (newvc - oldvc)]
        if not verifyFunc(usernew):
            for entry in difference:
                for cnt, fentry in enumerate(table):
                    if entry == fentry:
                        disable[cnt] = True
                        break
        
    return header, table, disable

def writerev(newrev, operation):
    libfile.put("lastrev", operation, newrev)
    
