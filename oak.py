# -*- coding: utf-8 -*-

import sys, os, re, time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try: from lib import preload
except:
    print "Cannot import preload. Exit!"
    sys.exit()

import query, userlib
from lib import libdate
import wikipedia as pywikibot
import pagegenerators, movepages

site = pywikibot.getSite()

generator = pagegenerators.PrefixingPageGenerator(prefix = u"รายชื่อตอนของ")

for i in generator:
    if re.search(u"รายชื่อตอนของ(\s+)?\w", i.title()):
        newname = re.sub(u"รายชื่อตอนของ(\s+)?", u"รายชื่อตอนใน ", i.title())
    else:
        newname = re.sub(u"รายชื่อตอนของ(\s+)?", u"รายชื่อตอนใน", i.title())
    print "old:", i.title()
    print "new:", newname
    bot = movepages.MovePagesBot(None, None, True, False, True, u"โรบอต: ย้ายจาก ของ มาเป็น ใน เพื่อให้อ่านง่าย")
    bot.moveOne(i, newname)
