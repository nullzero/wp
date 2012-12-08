# -*- coding: utf-8  -*-

import utility
import wikipedia as pywikibot
import pagegenerators, query, sys, datetime

# constant
LIMIT = 500
NUMQUERY = '5000'
CONST = 50
PATH = u"วิกิพีเดีย:รายชื่อชาววิกิพีเดียที่แก้ไขมากที่สุด_500_อันดับ"
BOTSUFFIX = u"_(รวมบอต)"
# end constant

site = pywikibot.getSite()

globalparams = {
    'action'  : 'query',
    'meta'    : 'globaluserinfo',
    'guiprop' : 'groups'
}

def isbot(data):
    if 'bot' in data['groups']: return True
    globalparams['guiuser'] = data['name']
    try: getdata = query.GetData(globalparams, site)
    except: return False
    try: return 'Global_bot' in getdata['query']['globaluserinfo']['groups']
    except: return False

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
    pywikibot.output(u"start!")
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
        
        print loop, getdata['query']['allusers'][0]['name']
        
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

if __name__ == "__main__":
    try:
        pywikibot.handleArgs(u"-log")
        main()
    finally:
        pywikibot.stopme()
