# -*- coding: utf-8 -*-

import re, sys, time, os, traceback
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try: from lib import preload
except:
    print "Cannot import preload. Exit!"
    sys.exit()

from lib import miscellaneous
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
    for i in range(1, libdate.getNumDay(today.year, today.month) + 1):
        pageName = u"แม่แบบ:เหตุการณ์ปัจจุบัน/%d_%s_%d" % (year, month, i)
        if not miscellaneous.existPage(pageName):
            pywikibot.output(u"Create day %d" % i)
            page = pywikibot.Page(site, pageName)
            page.put(
u"""{{เหตุการณ์ปัจจุบัน/วันเดือนปี|%d|%d|%d}}

<!-- ข่าวอยู่เหนือบรรทัดนี้ -->|}""" % (today.year, today.month, i)
                , u"เตรียมเหตุการณ์วันที่ %d %s %d ด้วยบอต" % (i, month, year))
        
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
    
    pageName = u"%s_พ.ศ._%d" % (month, year)
    if not miscellaneous.existPage(pageName):
        page = pywikibot.Page(site, pageName)
        content = u"""'''%s พ.ศ. %d''' เป็นเดือนที่ %d ของปี [[พ.ศ. %d]] \
วันแรกของเดือนเป็น[[%s]] วันสุดท้ายของเดือนเป็น[[%s]]

== [[สถานีย่อย:เหตุการณ์ปัจจุบัน]] ==
{{เหตุการณ์ปัจจุบัน/เดือน|%d %s}}

{{เหตุการณ์เดือนอื่น}}

[[หมวดหมู่:พ.ศ. %d แบ่งตามเดือน|*%d-%d]]

[[en:%s %d]]""" % (month, year, today.month, year, 
    libdate.weekdayThai(libdate.date(today.year, today.month, 1).weekday()),
    libdate.weekdayThai(libdate.date(today.year, today.month, 
        libdate.getNumDay(today.year, today.month)).weekday()),
    year, month,
    year, year, today.month,
    libdate.monthEng(today.month), today.year)
        page.put(content, u"เพิ่มเดือนโดยบอต")
        pywikibot.output(u"Write new month")
    else:
        pywikibot.output(u"Nothing to do!")
    
    pywikibot.output(u"'calendar script' terminated. (%s)" % libdate.getTime())
    pywikibot.stopme()
