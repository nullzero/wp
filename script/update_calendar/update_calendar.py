# -*- coding: utf-8 -*-

import re, sys, time, os, traceback
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try: from lib import preload
except:
    print "Cannot import preload. Exit!"
    sys.exit()

from lib import libdate
import wikipedia as pywikibot

site = pywikibot.getSite()

if __name__ == "__main__":
    pywikibot.handleArgs("-log")
    pywikibot.output(u"'calendar script' is invoked. (%s)" % libdate.getTime())
    
    today = libdate.date.today()
    year = today.year + 543    
    month = libdate.monthThai(today.month)
    day = today.day
    
    if today.year % 400 == 0: what = 29
    elif today.year % 100 == 0: what = 28
    elif today.year % 4 == 0: what = 29
    else: what = 28
        
    numdays = [31, what, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    content = u"""<!--แม่แบบนี้ถูกสร้างขึ้นโดยอัตโนมัติด้วยบอต การเปลี่ยนแปลงในหน้านี้จะถูกเขียนทับในวันต่อไป หากต้องการแก้ไข กรุณาแจ้ง ผู้ใช้:Jutiphan และต้นแบบได้ที่ แม่แบบ:กล่องเหตุการณ์ปัจจุบัน/ต้นแบบ -->
{| class="infobox" width="250" style="text-align: center; margin-top:7px; border:2px solid #cedff2;"
|- style="background-color: #cedff2"
| style="padding: 5px 0px; font-size:90%%" | '''วันที่''' [[{{LOCALDAY}} {{LOCALMONTHNAME}}]] &nbsp;|&nbsp; '''เวลา''' {{LOCALTIME}} น. {{purge|↑}}
|}

{| class="infobox" width="250" style="text-align: center; background-color: #f5faff; border:2px solid #cedff2;"
|- style="background-color: #cedff2"
| style="padding-top: 5px; padding-bottom: 5px" | [[%s พ.ศ. %d|<<]]
| colspan=5 style="padding: 5px 0px" | '''[[%s พ.ศ. %d|%s %d]]'''
| style="padding-top: 5px; padding-bottom: 5px" | [[%s พ.ศ. %d|>>]]
|-
|จ
|อ
|พ
|พฤ
|ศ
|ส
|อา
|-
""" % (libdate.monthThai(today.month - 1),
    year - 1 if today.month == 1 else year, 
    month, 
    year, 
    month, 
    year, 
    libdate.monthThai(today.month + 1),
    year + 1 if today.month == 12 else year)
    
    numblank = libdate.date(today.year, today.month, 1).weekday()
    for i in range(numblank): content += u"|\n"
    now = numblank
    for i in range(1, numdays[today.month - 1] + 1):
        if now % 7 == 0: content += u"|-\n"
        content += u"|'''[[%s|%d]]'''\n" % (u"แม่แบบ:เหตุการณ์ปัจจุบัน/%d_%s_%d" % (
            year, libdate.monthThai(today.month), i), i)
            
        now += 1
        
    while now % 7 != 0:
        content += u"|\n"
        now += 1
    
    content += u"|-\n|-\n|}"
    page = pywikibot.Page(site, u"แม่แบบ:กล่องเหตุการณ์ปัจจุบัน")
    
    if content == page.get():
        pywikibot.output(u"Nothing to do!")
    else:
        pywikibot.output(u"Write new calendar")
        page.put(content, u"อัปเดตปฏิทินโดยบอต")
        
    pywikibot.output(u"'calendar script' terminated. (%s)" % libdate.getTime())
    pywikibot.stopme()
