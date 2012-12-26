# -*- coding: utf-8 -*-

import sys, os, re, time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try: from lib import preload
except:
    print "Cannot import preload. Exit!"
    sys.exit()

import query, userlib, traceback
from lib import libdate
import wikipedia as pywikibot
import pagegenerators, movepages

site = pywikibot.getSite()

generator = pagegenerators.PrefixingPageGenerator(prefix = u"รายชื่อตอนของ")

for i in generator:
    print u"Checking %s" % i.title()
    if re.search(u"รายชื่อตอนของ", i.title()):
        try: i.get()
        except pywikibot.IsRedirectPage:
            gen = pagegenerators.ReferringPageGenerator(i)
            cnt = 0
            for x in gen: cnt += 1
            if cnt == 0:
                print u"Detected"
                try: i.put(u"{{ลบ|หน้า redirect ที่ 1) ชื่อผิดหลักการตั้งชื่อบทความ 2) ไม่มีหน้าลิงก์เข้า}}", u"โรบอต: ลบหน้าเปลี่ยนทางไม่จำเป็นและผิดหลักการตั้งชื่อ", force = True)
                except:
                    var = traceback.format_exc()
                    pywikibot.output(var.decode("utf-8"))

"""
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
    gen = pagegenerators.ReferringPageGenerator(i)
    for x in gen:
        print x.title()
        try: oldcontent = x.get()
        except pywikibot.IsRedirectPage: pass
            
        content = oldcontent.replace(u"รายชื่อตอนของ", u"รายชื่อตอนใน")
        content = re.sub(u"รายชื่อตอนใน(\s+)?", u"รายชื่อตอนใน", content)
        content = re.sub(u"รายชื่อตอนใน(?=\w)", u"รายชื่อตอนใน ", content)
        pywikibot.showDiff(oldcontent, content)
        if oldcontent != content:
            try: x.put(content, u"แก้ ของ มาเป็น ใน เพื่อให้อ่านง่ายขึ้น")
            except: pass
        
    #bot = movepages.MovePagesBot(None, None, True, False, True, u"โรบอต: ย้ายจาก ของ มาเป็น ใน เพื่อให้อ่านง่าย")
    #bot.moveOne(i, newname)
"""
