# -*- coding: utf-8  -*-

try: import utility
except: pass

import wikipedia as pywikibot
import pagegenerators, query, sys, datetime, re

# constant
LIMIT = 500
NUMQUERY = '5000'
CONST = 50
PATH = u"วิกิพีเดีย:รายชื่อชาววิกิพีเดียที่แก้ไขมากที่สุด_500_อันดับ"
BOTSUFFIX = u"_(รวมบอต)"
# end constant

site = pywikibot.getSite()
pbot = re.compile('^(.*(บอต|bot)|(บอต|bot).*)$', re.IGNORECASE)

def isbot(data):
    if 'bot' in data['groups']: return True
    if data['name'] == u'New user message': return True
    return pbot.match(data['name']) is not None

def trimbot(data):
    appendlist = []
    
    for i in data:
        if not isbot(i):
            appendlist.append(i)
    
    return appendlist

def dowrite(path, data):
    puttext = u"ปรับปรุงล่าสุด %s\n\n{{/begin|500}}\n" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cnt = 1
    
    for i in data:
        s = u"|-\n| %d || [[User:%s|%s]] %s %s || [[Special:Contributions/%s|%s]]\n" % (
            cnt, 
            i['name'], 
            i['name'], 
            '(Admin)' if ('sysop' in i['groups']) else '', 
            '(Bot)' if ('bot' in i['groups']) else '', 
            i['name'], 
            i['editcount'])

        puttext += s
        cnt += 1
    
    page = pywikibot.Page(site, path)
    gettext = page.get(get_redirect = True)
    
    pre, post = gettext.split(u'{{/end}}')
    
    page.put(puttext + u"{{/end}}\n" + post, u'ปรับปรุงรายการ')
    pywikibot.output(u"done!")
    
def main():
    pywikibot.output(u"'Most-edits' is invoked. (%s)" % 
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    includebot = []
    excludebot = []

    params = {
        'action'  : 'query',
        'list'    : 'allusers',
        'aulimit' : NUMQUERY,
        'auprop'  : 'editcount|groups',
    }
    
    loop = 0
        
    while True:
        try: getdata = query.GetData(params, site)
        except: break
            
        includebot += getdata['query']['allusers']
        excludebot += trimbot(getdata['query']['allusers'])
        
        pywikibot.output("%d" % loop)
        pywikibot.output(getdata['query']['allusers'][0]['name'])
        
        loop += 1
        
        try: params['aufrom'] = getdata['query-continue']['allusers']['aufrom']
        except: break
        
        if loop % CONST == 0:
            includebot.sort(key = lambda datall: int(datall['editcount']), reverse = True)
            excludebot.sort(key = lambda datall: int(datall['editcount']), reverse = True)
            
            del includebot[LIMIT:]
            del excludebot[LIMIT:]
            
    includebot.sort(key = lambda datall: int(datall['editcount']), reverse = True)
    excludebot.sort(key = lambda datall: int(datall['editcount']), reverse = True)
    
    del includebot[LIMIT:]
    del excludebot[LIMIT:]
    
    dowrite(PATH + BOTSUFFIX, includebot)
    dowrite(PATH, excludebot)
    
    pywikibot.output(u"'Most-edits' terminated. (%s)" % 
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    try:
        pywikibot.handleArgs(u"-log")
        main()
    finally:
        pywikibot.stopme()
