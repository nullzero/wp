# -*- coding: utf-8  -*-

import sys, re

try: import preload
except:
    print "เรียกใช้ไลบรารีไม่ได้ จบการทำงาน!"
    sys.exit()

import wikipedia as pywikibot
import query

site = preload.site

def getRevision(revid, prop):
    params = {
        'action'   : 'query',
        'prop'     : 'revisions',
        'revids'   : revid,
    }
    if prop == 'diff':
        params['rvdiffto'] = 'prev'
        return query.GetData(params, site)['query']['pages'].itervalues().next()
    elif prop == 'content':
        params['rvprop'] = 'content'
        return query.GetData(params, site)['query']['pages'].itervalues().next()['revisions'][0]['*']
