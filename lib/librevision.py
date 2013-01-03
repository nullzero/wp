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

def allContribute(pageName):
    params = {
        'action'   : 'query',
        'prop'     : 'revisions',
        'titles'   : pageName,
        'rvprop'   : 'user|ids',
        'rvlimit'  : 5000
    }
    return query.GetData(params, site)['query']['pages'].itervalues().next()['revisions']

def revert(pageid, revid, summary, title):
    params = {
        'action': 'edit',
        'pageid': pageid,
        'undo'  : revid,
        'summary': summary + preload.summarySuffix,
        'token'  : site.getToken(),
        'minor'  : 1,
    }
    
    response, data = query.GetData(params, site, back_response = True)
    
    try:
        if data['edit']['result'] == u"Success":
            pywikibot.output(u"ย้อน %s สำเร็จ!" % title)
        else:
            raise Exception
    except:
        print response, data
        pywikibot.output(u"ย้อน %s ไม่สำเร็จ" % title)
