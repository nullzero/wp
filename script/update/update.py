# -*- coding: utf-8 -*-

import sys, os, re
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
    pywikibot.output(u"'update script' is invoked. (%s)" % libdate.getTime())
    
    today = libdate.date.today()
    year = today.year + 543
    month = libdate.monthThai(today.month)
    day = today.day
    
    page = pywikibot.Page(site, u"แม่แบบ:วันสำคัญ")
    content = page.get()
    
    pat = re.compile(u"\n\*\ \[\[(.*?)\ (.*?)\]\]\ :\ (.*)")
    result = pat.finditer(content)
    
    saveall = []
    
    for i in result:
        nday = 0 if i.group(1) == u'?' else int(i.group(1))
        nmonth = i.group(2)
        ncon = i.group(3).split(u',')
        nins = []
        for dat in ncon:
            dat = dat.strip()
            yeardat = re.search(u"\{\[\[(.*)\]\]\}", dat)
            if yeardat is not None:
                if int(yeardat.group(1)[len(u"พ.ศ. "):]) == year:
                    yeardat = re.sub(u"\{\[\[.*\]\]\}", u"", dat).strip()
                    nins.append(yeardat)
            else:
                nins.append(dat)
        
        for j in range(1, 12 + 1):
            if libdate.monthThaiAbbr(j) == nmonth:
                nmonth = j
                break
            
        if len(nins) != 0: saveall.append((nday, nmonth, u", ".join(nins)))
    
    for idx, (nday, nmonth, ncon) in enumerate(saveall):
        if(nmonth, nday) >= (today.month, today.day): break
    
    wcontent = u"""<!-- ข้อมูลในหน้านี้อัปเดตโดยอัตโนมัติด้วยบอต กรุณาแก้ที่ แม่แบบ:วันสำคัญ -->
==== วันสำคัญที่ผ่านมา ====
"""
    for i in range(idx - 3, idx):
        state = i < 0
        wcontent += u"* [[%s %s]] : %s\n" % (u'?' if saveall[i][0] == 0 else str(saveall[i][0]), 
                                            libdate.monthThaiAbbr(saveall[i][1]), saveall[i][2])
    
    wcontent += u"==== วันสำคัญที่กำลังจะมาถึง ====\n"
    
    for i in range(idx, idx + 3):
        ip = i % len(saveall)
        state = i >= len(saveall)
        wcontent += u"* [[%s %s]] : %s\n" % (u'?' if saveall[ip][0] == 0 else str(saveall[ip][0]), 
                                            libdate.monthThaiAbbr(saveall[ip][1]), saveall[ip][2])
    
    wcontent = wcontent[:-1]
    page = pywikibot.Page(site, u"แม่แบบ:เหตุการณ์ปัจจุบัน/วันสำคัญ")
    
    if page.get() == wcontent:
        pywikibot.output(u"Nothing to do!")
    else:
        pywikibot.output(u"Write new event")
        page.put(wcontent, u"อัปเดตรายชื่อวันสำคัญโดยบอต", force = True)
        
    pywikibot.output(u"'update script' terminated. (%s)" % libdate.getTime())
    pywikibot.stopme()
