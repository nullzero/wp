# -*- coding: utf-8 -*-

import re, sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try: from lib import preload
except:
    print "Cannot import preload. Exit!"
    sys.exit()

import wikipedia as pywikibot
pywikibot.handleArgs("-family:wikibooks")
pywikibot.handleArgs("-user:Nullzero")
import pagegenerators, movepages
import re

movebot = movepages.MovePagesBot(None, None, False, False, True, u"รวมเล่มเข้าตำรา")
mainPageName = u"ตำราหมากล้อม"
mainPage = pywikibot.Page(pywikibot.getSite(), mainPageName)
gen = pagegenerators.LinkedPageGenerator(mainPage)

for page in gen:
    movebot.moveOne(page, mainPageName + u"/" + page.title())
