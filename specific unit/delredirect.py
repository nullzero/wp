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

import pagegenerators
import re

#gen = pagegenerators.AllpagesPageGenerator(includeredirects = 'only', namespace = u"|".join([str(x) for x in range(1, 17, 2)]))
#gen = pagegenerators.AllpagesPageGenerator(includeredirects = 'only', namespace = 0)
gen = pagegenerators.PrefixingPageGenerator(u"ชั้นหนังสือ", includeredirects = 'only')

for page in gen:
    cnt = 0
    genall = pagegenerators.ReferringPageGenerator(page, followRedirects=True)
    for pageref in genall: cnt += 1
    genall = pagegenerators.ReferringPageGenerator(page)
    for pageref in genall: cnt += 1
    if cnt == 0:
        print ">>>", page.title()
        page.delete(u"ลบหน้าเปลี่ยนทางไม่จำเป็น", True, throttle = False)
        #page.put(u"{{ลบ|หน้าเปลี่ยนทางไม่จำเป็น}}", u"หน้าเปลี่ยนทางไม่จำเป็น", force = True)

"""
genall = pagegenerators.ReferringPageGenerator(page)
for pageref in genall:
    print "processing", pageref.title()
    try: ocontent = pageref.get()
    except: continue
    content = process(ocontent, page.title(), u"{{วิกิตำรา:ชั้นหนังสือ/")
    if ocontent != content:
        pywikibot.showDiff(ocontent, content)
        try: pageref.put(content, u"เก็บกวาด", force = True)
        except: pass
"""
