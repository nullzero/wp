# -*- coding: utf-8 -*-

DEBUG = False

import sys, os, re, time, traceback, urllib, subprocess
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try: from lib import preload
except:
    print "เรียกใช้ไลบรารีไม่ได้ จบการทำงาน!"
    sys.exit()

import query, userlib
from lib import libdate, liblang, libstring, libgenerator, librevision, miscellaneous
import wikipedia as pywikibot

site = preload.site
env = preload.env

def firstContributor():
    return NotImplemented

def pagestat():
    allpages = []
    for page in site.allpages(includeredirects = False):
        print ">>>", page.title()
        params = {
            'action': 'query',
            'prop': 'revisions',
            'titles': page.title(),
            'rvprop': 'ids',
            'rvlimit': 5000,
        }
        cnt = 0
        while True:
            dat = query.GetData(params, site)
            cnt += len(dat['query']['pages'].itervalues().next()['revisions'])
            if 'query-continue' in dat:
                params['rvstartid'] = dat['query-continue']['revisions']['rvcontinue']
            else:
                break
        allpages.append((cnt, page.title()))
        
        if len(allpages) > 100000:
            allpages = sorted(allpages, key=lambda x: x[0], cmp=lambda a, b: b - a)
            del allpages[100000:]

    return sorted(allpages, key=lambda x: x[0], cmp=lambda a, b: b - a)

def getdat(title):
    

def main():
    #allpages = pagestat()
    oldtable = getdat(u"บทความแก้ไขมากสุด")
    oldtablelist = getdat(u"บทความรายชื่อแก้ไขมากสุด")
    table = []
    tablelist = []
    ptr = 0
    """
    while incomplete(table, tablelist):
        if u"รายชื่อ" in allpage[ptr][1]:
            rankold = getrankold(allpage[ptr][1], oldtablelist)
            tablelist.append(allpage[ptr][1], rankold, allpage[ptr][0])
        else:
            rankold = getrankold(allpage[ptr][1], oldtable)
            table.append(allpage[ptr][1], rankold, allpage[ptr][0])
    writetable(table, u"บทความแก้ไขมากสุด")
    writetable(tablelist, u"บทความรายชื่อแก้ไขมากสุด")
    
    longpage = getdat(u"บทความยาวสุด")
    """
    
main()
