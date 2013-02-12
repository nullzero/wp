# -*- coding: utf-8 -*-

import sys, os, re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try: from lib import preload
except:
    print "เรียกใช้ไลบรารีไม่ได้ จบการทำงาน!"
    sys.exit()

import wikipedia as pywikibot
import catlib, pagegenerators

site = preload.site

lock = True

for cat in site.allpages(namespace = 14):
    print cat.title()
    if cat.title().startswith(u"หมวดหมู่:พ.ศ."): lock = False
    if lock: continue
    catname = re.search(u"(?<=:)(.*)", cat.title()).group(1)
    if ord(catname[0]) <= 128: continue
    if u"พ.ศ." in catname or u"ค.ศ." in catname: continue
    print cat.title()
    try:
        page = pywikibot.Page(site, catname)
        if not page.exists(): continue
        if str(catlib.Category(site, cat.title())) not in [str(i) for i in page.categories()]:
            catlib.add_category(page, cat, u"เพิ่มหมวดหมู่")
            page = pywikibot.Page(site, catname)
            content = page.get()
            if u"[[Category:" in content:
                page.put(content.replace(u"[[Category:", u"[[หมวดหมู่:"), u"เก็บกวาด")
    except:
        pass
    try:
        print "a"
        content = cat.get()
        if re.search(u"\{\{(?:ดูเพิ่ม|Catmain|Catmore|Cat main)", content, flags = re.IGNORECASE) is None:
            cat.put(u'{{ดูเพิ่ม}}\n' + content, u"เพิ่มแม่แบบดูเพิ่ม")
    except:
        pass
pywikibot.stopme()
