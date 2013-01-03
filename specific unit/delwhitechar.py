# -*- coding: utf-8 -*-

import re, sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try: from lib import preload
except:
    print "Cannot import preload. Exit!"
    sys.exit()

import wikipedia as pywikibot
pywikibot.handleArgs("-family:wikibooks")
import pagegenerators, movepages
import re

gen = pagegenerators.AllpagesPageGenerator()
cntpage = 0
ask = True

for page in gen:
    try: ocontent = page.get()
    except: continue
    
    print u"I'm checking " + page.title()
    
    content = ocontent
    check = u"แโใไะาๅำัิีึืํฺุู็่้๊๋์ฯ"
    
    for i in check:
        content = re.sub(i + u"+", i, content)
    
    content = re.sub(u'<\s*font.*?color.*?#ffffff.*?>.*?<\s*/\s*font\s*>', u'\n', content)
    content = re.sub(u'<.*?>', u'', content)
    content = re.sub(u'\[\[(\s+)?(.*?)(\s+)?\]\]', u'[[\g<2>]]', content)
    content = re.sub(u'^[ \t\r\f\v]+', u'', content, re.MULTILINE)
    content = re.sub(u'^\n\n\n*', u'\n\n', content, re.MULTILINE)
    content = re.sub(u'^\d+\.', u'#', content, re.MULTILINE)
    content = re.sub(u'^#(.*?)\n\s+', u'#\g<1>\n', content, re.MULTILINE)
    
    if content != ocontent:
        try:
            page.put(content, u"โรบอต: เก็บกวาด", force = True)
        except:
            pass
    
    cntpage += 1
    if cntpage % 10 == 0 and ask:
        s = raw_input("Continue?")
        if s == "n": break
        elif s == "a": ask = False
