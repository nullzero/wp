# -*- coding: utf-8  -*-

import sys, time

try: import preload
except:
    print "Cannot import preload. Exit!"
    sys.exit()

import pagegenerators, query
import wikipedia as pywikibot

site = preload.site

def CatGenerator(catname):
    return pagegenerators.GeneratorFactory().getCategoryGen(u':' + catname, 0)

def recentchanges(number = 100, rcstart = None, rcend = None, rcshow = ['!redirect', '!bot'],
    rcdir = 'older', rctype = 'edit|new', namespace = None, repeat = False, user = None):
    params = {
        'action'    : 'query',
        'list'      : 'recentchanges',
        'rcdir'     : rcdir,
        'rctype'    : rctype,
        'rcprop'    : ['user', 'comment', 'timestamp', 'title', 'ids',
                       'loginfo', 'sizes'], #', 'flags', 'redirect', 'patrolled'],
        'rcnamespace' : namespace,
        'rclimit'   : int(number),
    }
    
    if user: params['rcuser'] = user
    if rcstart: params['rcstart'] = rcstart
    if rcend: params['rcend'] = rcend
    if rcshow: params['rcshow'] = rcshow
    if rctype: params['rctype'] = rctype

    seen = set()
    while True:
        data = query.GetData(params)
        if 'error' in data:
            raise RuntimeError('%s' % data['error'])
        try:
            rcData = data['query']['recentchanges']
        except KeyError:
            raise ServerError("The APIs don't return data, the site may be down")

        for i in rcData:
            if i['revid'] not in seen:
                seen.add(i['revid'])
                page = pywikibot.Page(site, i['title'], defaultNamespace=i['ns'])
                if 'comment' in i:
                    page._comment = i['comment']
                yield page, i
                
        if not repeat: break
        time.sleep(10.0)
