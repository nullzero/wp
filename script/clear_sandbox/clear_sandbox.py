# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try: from lib import preload
except:
    print "Cannot import preload. Exit!"
    sys.exit()

from lib import libdate
import wikipedia as pywikibot

if __name__ == "__main__":
    pywikibot.handleArgs(u"-log")
    pywikibot.output(u"'clear-sandbox' is invoked. (%s)" % libdate.getTime())
            
    vlist = []
#    vlist.append(u"วิกิพีเดีย:สอนการใช้งาน_(จัดรูปแบบ)/กระดาษทด")
#    vlist.append(u"วิกิพีเดีย:สอนการใช้งาน_(แหล่งข้อมูลอื่น)/กระดาษทด")
#    vlist.append(u"วิกิพีเดีย:สอนการใช้งาน_(แก้ไข)/กระดาษทด")
#    vlist.append(u"วิกิพีเดีย:สอนการใช้งาน_(วิกิพีเดียลิงก์)/กระดาษทด")
    vlist.append(u"วิกิพีเดีย:ทดลองเขียน")

    site = pywikibot.getSite()
    text = u"{{ทดลองเขียน}}<!-- กรุณาอย่าแก้ไขบรรทัดนี้ ขอบคุณครับ/ค่ะ -- Please leave this line as they are. Thank you! -->\n"

    for i in vlist:
        page = pywikibot.Page(site, i)
        page.put(text, u"ล้างหน้าอัตโนมัติด้วยบอต")

    pywikibot.output(u"'clear-sandbox' terminated. (%s)" % libdate.getTime())
    pywikibot.stopme()
