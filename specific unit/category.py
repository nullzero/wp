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

site = pywikibot.getSite()

openoffice = pywikibot.Page(site, u"OpenOffice")
gen = openoffice.linkedPages()

for i in gen:
    print u"process" + i.title()
    content = i.get()
    if re.search(u"==\s*ดูเพิ่ม\s*==", content) is not None:
        content = re.sub(u"==\s*ดูเพิ่ม\s*==.*", u"", content, flags = re.DOTALL)
    
    if re.search(u"\[\[หมวดหมู่:", content) is not None:
        content = re.sub(u"\[\[หมวดหมู่:.*", u"", content, flags = re.DOTALL)
        
    content += u"\n[[หมวดหมู่:OpenOffice]]"
    content = re.sub(u"[ \t\r\f\v]+$", u"", content, flags = re.MULTILINE)
    content = re.sub(u"\n\n\n\n*", u"\n\n\n", content)
    if content != i.get():
        i.put(content, u"จัดหมวดหมู่", force = True)
