# -*- coding: utf-8  -*-

import sys, re

try: import preload
except:
    print "เรียกใช้ไลบรารีไม่ได้ จบการทำงาน!"
    sys.exit()

import pwikipedia as pywikibot
from lib import libstring

"""
ใช้แปลงข้อมูล wikitable มาเป็น list ข้อมูล
ข้อจำกัด:
- ใช้ได้กับเฉพาะตารางที่ไม่มี markup พิเศษ เช่น rowspan align (ยกเว้นกรณี markup ทั้งตารางที่สามารถมีได้)
  - อาจรองรับ row/col span ในภายหลัง
- ไม่มี caption |+
- มีหัวตารางอยู่บนสุดเพียงบรรทัดเดียวเท่านั้น
- ตารางข้อมูลต้องครบทุกช่อง

"""

class TableError(pywikibot.Error):
    pass
    
def wiki2table(content, tag):
    obj = re.search(ur"(?s)" + re.escape(tag[0]) + ur"(.*?)" + re.escape(tag[1]), content)
    if not obj: raise TableError

    content = obj.group(1)
    content = libstring.repSub(ur"(?m)(^\!.*?)\!\!", u"\\1\n!", content)
    content = libstring.repSub(ur"(?m)(^\|.*?)\|\|", u"\\1\n|", content)
    header = []
    lines = content.split(u"\n")
    
    for line in lines:
        if line.startswith(u"!"):
            header.append(line[1:].strip())
    
    table = []
    linelist = []
    
    for line in lines:
        if line.startswith(u"|-"):
            if linelist:
                table.append(linelist)
                linelist = []
        elif line.startswith(u"|}"):
            if linelist:
                table.append(linelist)
                linelist = []
        elif line.startswith(u"|"):
            linelist.append(line[1:].strip())
    
    for line in table:
        if len(line) != len(header): raise TableError
    
    header = (re.search(ur"(?m)^\{\|.*?$", content).group(), header)
    return header, table
