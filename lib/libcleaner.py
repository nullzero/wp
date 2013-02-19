# -*- coding: utf-8  -*-
"""
This library 
"""

import sys, os, re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try: from lib import preload
except:
    print "เรียกใช้ไลบรารีไม่ได้ จบการทำงาน!"
    sys.exit()

from lib import liblang
import wikipedia as pywikibot

def dellink(s):
    s = s.group()
    s = re.sub(u"'''", u"", s)
    s = re.sub(u"''", u"", s)
    s = re.sub(u"<(?!/?(ref|sup|sub)).*?>", u"", s)
    return s.strip()

def wikitable(s):
    s = s.group()
    s = re.sub(u"^(\|[\-\+\}]?)[ \t\r\f\v]*", u"\g<1> ", s, flags = re.MULTILINE)
    s = re.sub(u"[ \t\r\f\v]*\|\|[ \t\r\f\v]*", u" || ", s)
    s = re.sub(u"[ \t\r\f\v]*!![ \t\r\f\v]*", u" !! ", s)
    s = re.sub(u"^\|([\}\-$])[ \t\r\f\v]*$", u"|\g<1>", s, flags = re.MULTILINE)
    s = re.sub(u"^![ \t\r\f\v]*", u"! ", s, flags = re.MULTILINE)
    return s

def consecutiveSpace(s):
    return re.sub(u"[ \t\r\f\v]+", u" ", s.group())

def clean(s):
    s = liblang.fixRepetedVowel(s)
    s = re.sub(u"_(?=[^\[\]]*\]\])", u" ", s)
    s = re.sub(u"(?<!=)[ \t\r\f\v]+$", u"", s, flags = re.MULTILINE)
    s = re.sub(u"=$", u"= ", s, flags = re.MULTILINE)
    s = re.sub(u"^(=+)[ \t\r\f\v]*(.*?)[ \t\r\f\v]*(=+)[ \t\r\f\v]*$", u"\g<1> \g<2> \g<3>", s, flags = re.MULTILINE)
    s = re.sub(u"^= (.*?) =$", u"== \g<1> ==", s, flags = re.MULTILINE)
    s = re.sub(u"^==+\ .*?\ ==+$", dellink, s, flags = re.MULTILINE)
    s = re.sub(u"(rowspan|align|colspan|width)[ \t\r\f\v]*=[ \t\r\f\v]*", u"\g<1> = ", s)
    s = re.sub(u"\[\[(.?)[Cc]ategory:", u"[[\g<1>หมวดหมู่:", s)
    s = re.sub(u"\[\[(.?)([Ii]mage|[Ff]ile|ภาพ):", u"[[\g<1>ไฟล์:", s)
    s = re.sub(u"==[ \t\r\f\v]*(แหล่ง|หนังสือ|เอกสาร|แหล่งข้อมูล)อ้างอิง[ \t\r\f\v]*==", u"== อ้างอิง ==", s)
    s = re.sub(u"==[ \t\r\f\v]*(หัวข้ออื่นที่เกี่ยวข้อง|ดูเพิ่มที่)[ \t\r\f\v]*==", u"== ดูเพิ่ม ==", s)
    s = re.sub(u"==[ \t\r\f\v]*(เว็บไซต์อื่น|(เว็บไซต์|โยง|ลิงก์|ลิงค์|Link\ |ข้อมูล|แหล่งข้อมูล)ภายนอก)[ \t\r\f\v]*==",
        u"== แหล่งข้อมูลอื่น ==", s)
    s = re.sub(u"^(:*)([#\*]+)[ \t\r\f\v]*", u"\g<1>\g<2> ", s, flags = re.MULTILINE)
    s = re.sub(u"^(:+)(?![\*#])[ \t\r\f\v]*", u"\g<1> ", s, flags = re.MULTILINE)
    s = re.sub(u"\[\[[ \t\r\f\v]*(.*?)[ \t\r\f\v]*\]\]", u"[[\g<1>]]", s)
    s = re.sub(u"^\|(?![\}\+\-])[ \t\r\f\v]*", u"| ", s, flags = re.MULTILINE)
    s = re.sub(u"^\{\|.*^\|\}.*?$", wikitable, s, flags = re.DOTALL | re.MULTILINE)
    s = re.sub(u"<references[ \t\r\f\v]*/[ \t\r\f\v]*>", u"{{รายการอ้างอิง}}", s, flags = re.MULTILINE)
    s = re.sub(u"\{\{[ \t\r\f\v]*Reflist[ \t\r\f\v]*", u"{{รายการอ้างอิง", s, flags = re.MULTILINE | re.IGNORECASE)
    s = re.sub(u"^(?![ \t\r\f\v]).*?$", consecutiveSpace, s, flags = re.MULTILINE)
    s = re.sub(u"(?m)^(:+)\ +\{\|", u"\g<1>{|", s)
    return s
