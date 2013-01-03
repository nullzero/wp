# -*- coding: utf-8 -*-
import sys, os, re, time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try: from lib import preload
except:
    print "Cannot import preload. Exit!"
    sys.exit()

"""

import query, userlib, traceback
from lib import libdate
import wikipedia as pywikibot
import pagegenerators, movepages

site = pywikibot.getSite()

generator = pagegenerators.PrefixingPageGenerator(prefix = u"รายชื่อตอนของ")

for i in generator:
    print u"Checking %s" % i.title()
    if re.search(u"รายชื่อตอนของ", i.title()):
        try: content = i.get()
        except pywikibot.IsRedirectPage:
            continue
        if re.search(u"\{\{ลบ", content) is None:
            print i.title()

"""
# -*- coding: utf-8 -*-
"""
import sys, os, re, time, traceback
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
    gen = pagegenerators.ReferringPageGenerator(i)
    for x in gen:
        print u"refer to " + x.title()
        try: oldcontent = x.get()
        except pywikibot.IsRedirectPage: continue
            
        content = oldcontent.replace(u"รายชื่อตอนของ", u"รายชื่อตอนใน")
        content = re.sub(u"รายชื่อตอนใน(\s+)?", u"รายชื่อตอนใน", content)
        content = re.sub(u"รายชื่อตอนใน(?=\w)", u"รายชื่อตอนใน ", content)
        pywikibot.showDiff(oldcontent, content)
        if oldcontent != content:
            try: x.put(content, u"แก้ ของ มาเป็น ใน เพื่อให้อ่านง่ายขึ้น", force = True)
            except: print traceback.format_exc()
    bot = movepages.MovePagesBot(None, None, True, False, True, u"โรบอต: ย้ายจาก ของ มาเป็น ใน เพื่อให้อ่านง่าย")
    bot.moveOne(i, newname)
"""
