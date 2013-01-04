# -*- coding: utf-8 -*-

import sys, os, re, time, traceback
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try: from lib import preload
except:
    print "เรียกใช้ไลบรารีไม่ได้ จบการทำงาน!"
    sys.exit()

import wikipedia as pywikibot

site = preload.site()

namespace = u"|".join([str(x) for x in range(1, 17, 2)])
includeredirects = "only"

gen = site.allpages(namespace=namespace, includeredirects=includeredirects)
for i in gen: i.put(u"{{ลบ|หน้าเปลี่ยนทางไม่จำเป็น}}", u"โรบอต: ลบหน้าเปลี่ยนทางไม่จำเป็น", force = True)
pywikibot.stopme()
