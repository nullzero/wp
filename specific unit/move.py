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

movebot = movepages.MovePagesBot(None, None, True, False, True, u"โรบอต: เปลี่ยนชื่อบทความเข้าบทความหลัก")

gen = pagegenerators.TextfilePageGenerator("movepagelist (wikibooks)")
cntpage = 0
ask = True

for page in gen:
    movebot.moveOne(page, u"OpenOffice/" + page.title())
    cntpage += 1
    if cntpage % 10 == 0 and ask:
        s = raw_input("Continue?")
        if s == "n": break
        elif s == "a": ask = False
