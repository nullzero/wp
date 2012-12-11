#-*-coding: utf-8 -*-

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try: import preload
except:
    print "Cannot import preload. Exit!"
    sys.exit()

import wikipedia as pywikibot
from datetime import date

if __name__ == "__main__":
    pywikibot.handleArgs("-log")
    pywikibot.output(u"'update script' is invoked. (%s)" % preload.getTime())
    today = date.today()
    year = today.year + 543
    month = [u"มกราคม", u"กุมภาพันธ์", u"มีนาคม", u"เมษายน", u"พฤษภาคม", u"มิถุนายน", 
            u"กรกฎาคม", u"สิงหาคม", u"กันยายน", u"ตุลาคม", u"พฤศจิกายน", u"ธันวาคม"][today.month - 1]
    day = today.day
    site = pywikibot.getSite() 
    page = pywikibot.Page(site, u"แม่แบบ:เหตุการณ์ปัจจุบัน/%d_%s_%d" % (year, month, day))
    
    try:
        page.get()
        pywikibot.output(u"The page has already created.")
    except pywikibot.NoPage:
        page.put(
u"""{{เหตุการณ์ปัจจุบัน/วันเดือนปี|%d|%d|%d}}

<!-- ข่าวอยู่เหนือบรรทัดนี้ -->|}""" % (today.year, today.month, today.day)
    , u"เตรียมเหตุการณ์วันที่ %d %s %d ด้วยบอต" % (day, month, year))
    
    pywikibot.output(u"'update script' terminated. (%s)" % preload.getTime())
    pywikibot.stopme()
