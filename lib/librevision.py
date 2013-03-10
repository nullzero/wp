# -*- coding: utf-8  -*-
"""
Manipulate revision.
"""

__version__ = "1.0.1"
__author__ = "Sorawee Porncharoenwase"

import preload
import query, pwikipedia as pywikibot

"""
quickCntRev
===========
Count all revisions quickly
"""
def quickCntRev(page):
    params = {
        'action': 'query',
        'prop': 'revisions',
        'titles': page.title(),
        'rvprop': 'ids',
        'rvlimit': 5000,
    }
    cnt = 0
    while True:
        dat = query.GetData(params, self.site)
        cnt += len(dat['query']['pages'].itervalues().next()['revisions'])
        if 'query-continue' in dat:
            params['rvstartid'] = dat['query-continue']['revisions']['rvcontinue']
        else:
            break
    return cnt


"""
getRevision
===========
Get text of given revision.
"""

def getRevision(revid, site=None):
    if site is None:
        site = pywikibot.getSite()
    params = {
        'action'   : 'query',
        'prop'     : 'revisions',
        'revids'   : revid,
    }
    return Page(site, query.GetData(params, site)['query']['pages']
                .itervalues().next()['title'])
