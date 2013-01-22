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

gen = pagegenerators.PrefixingPageGenerator(prefix = u"วิกิตำรา:ชั้นหนังสือ")
site = pywikibot.getSite()

always = False


for page in gen:
    genall = pagegenerators.ReferringPageGenerator(page, followRedirects=True)
    for pageref in genall:
        print "processing", pageref.title()
        try: ocontent = pageref.get()
        except: continue
        content = ocontent.replace(u"{{วิกิตำรา:ชั้นหนังสือ", u"{{ชั้นหนังสือ")
        if ocontent != content:
            pywikibot.showDiff(ocontent, content)
            try: pageref.put(content, u"เก็บกวาด", force = True)
            except: pass

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
