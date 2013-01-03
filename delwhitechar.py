# -*- coding: utf-8 -*-

import wikipedia as pywikibot
import pagegenerators, movepages
import re

pywikibot.handleArgs("-family:wikibooks")

gen = pagegenerators.AllpagesPageGenerator()
movebot = movepages.MovePagesBot(None, None, True, False, True, u"โรบอต: เปลี่ยนชื่อบทความมีสระซ้อน")

gen = [pywikibot.Page(pywikibot.getSite(), u"ขอความช่วยเหลือใน_OpenOffice.org")]

for page in gen:
    try: ocontent = page.get()
    except: continue
    
    print u"I'm checking " + page.title()
    
    content = ocontent
    check = u"แโใไะาๅำัิีึืํฺุู็่้๊๋์ฯ"
    
    for i in check:
        content = re.sub(i + u"+", i, content)
    
    if content != ocontent:
        try:
            page.put(content, u"โรบอต: เก็บกวาด")
        except:
            pass
    
    opagetitle = page.title()
    pagetitle = opagetitle
    
    for i in check:
        pagetitle = re.sub(i + u"+", i, pagetitle)
