# -*- coding: utf-8  -*-
"""
Clean! Clean! Clean!
"""

__version__ = "1.0.1"
__author__ = "Sorawee Porncharoenwase"

import sys, os, re
import preload
import pwikipedia as pywikibot
from lib import liblang

def sectionClean(s):
    """Helper function to clean section's title."""
    s = s.group()
    for pat in patListSection:
        s = pat[0].sub(pat[1], s)
    return s.strip()

def wikitableClean(s):
    """Helper function to clean wikitable."""
    s = s.group()
    for pat in patListTable:
        s = pat[0].sub(pat[1], s)
    return s

def consecutiveSpace(s):
    """Remove consecutive spaces."""
    return re.sub(u"[ \t\r\f\v]+", u" ".group())

def clean(s):
    """Clean text!"""
    s = liblang.fixRepetedVowel(s)
    for pat in patList:
        s = pat[0].sub(pat[1], s)
    return s

patList = []

patList.append((ur"[\t\r\f\v]", u" "))
# change all whitespaces to space!
patList.append((ur"_(?=[^\[\]]*\]\])", u" "))
# $[[_abc_def_]]$ => $[[ abc def ]]$
patList.append((ur"(?m)(?<!=) +$", u""))
# strip traling space
patList.append((ur"(?m)=$", u"= "))
# strip traling space except the last character is =
patList.append((ur"(?m)^(=+) *(.*?) *(=+) *$", ur"\1 \2 \3"))
# $==   oak   ==   $ => $== oak ==$
patList.append((ur"(?m)^= (.*?) =$", ur"== \1 =="))
# don't use first-level headings
patList.append((ur"(?m)^==+\ .*?\ ==+$", sectionClean))
"""call dellink!"""
tablemarkup = [u"rowspan", u"align", u"colspan", u"width", u"style"]
patList.append((u"(%s) *= *" % u"|".join(tablemarkup), ur"\1 = "))
# clean whitespace around equal sign
patList.append((ur"\[\[ *(.*?) *\]\]", ur"[[\1]]"))
# $[[   abc   def   ]]$ => $[[abc   def]]$
patList.append((ur"\[\[(:?)[Cc]ategory:", ur"[[\1หมวดหมู่:"))
# L10n
patList.append((ur"\[\[(:?)([Ii]mage|[Ff]ile|ภาพ):", ur"[[\1ไฟล์:"))
# L10n
patList.append((u"(?m)^== (แหล่ง|หนังสือ|เอกสาร|แหล่งข้อมูล)อ้างอิง ==$",
                u"== อ้างอิง =="))
# อ้างอิง
patList.append((u"(?m)^== (หัวข้ออื่นที่เกี่ยวข้อง|ดูเพิ่มที่) ==$",
                u"== ดูเพิ่ม =="))
# ดูเพิ่ม
patList.append((ur"""(?mx)^==\ (เว็บไซต์|โยง|ลิง[กค]์|Link *|(แหล่ง)?ข้อมูล)
                (ภายนอก|อื่น)\ ==$""", u"== แหล่งข้อมูลอื่น =="))
# แหล่งข้อมูลอื่น
patList.append((ur"(?m)^(:*)([#\*]+) *", ur"\1\2 "))
# clean whitespace after indentation and bullet
patList.append((ur"(?m)^(:+)(?![\*#]) *", ur"\1 "))
# clean whitespace after indentation and bullet
patList.append((ur"(?m)^(:*)([\*#]*) \{\|", ur"\1\2{|"))
# but openning tag of table must stick with front symbol
# "$:::** {|$" => "$:::**{|$"
patList.append((ur"(?m)^\|(?![\}\+\-]) *", u"| "))
# clean whitespace for template and table
# "$|asdasd$" => "$| asdasd$"
patList.append((u"(?ms)^\{\|.*^\|\}.*?$", wikitableClean))
"""call wikitable!"""
patList.append((u"<references */ *>", u"{{รายการอ้างอิง}}"))
# FIXME: call this on some pages makes reference error.
patList.append((u"(?i)\{\{ *Reflist *", u"{{รายการอ้างอิง"))
# L10n
#patList.append((u"(?m)^(?! ).*?$", consecutiveSpace))
# FIXME: source code!
""" Section ========================================================="""
patListSection = []

patListSection.append((u"'''", u""))
# remove all bold markup
patListSection.append((u"''", u""))
# remove all italic markup
patListSection.append((u"<(?!/?(ref|sup|sub)).*?>", u""))
# remove all html markup except refupub
""" Table ========================================================="""
patListTable = []

patListTable.append((ur"(?m)^(\|[\-\+\}]?) *", ur"\1 "))
patListTable.append((ur" *\|\| *", u" || "))
patListTable.append((u" *!! *", u" !! "))
patListTable.append((ur"(?m)^\|([\}\-$]) *$", ur"|\1"))
patListTable.append((u"(?m)^! *", u"! "))
    
for i, pat in enumerate(patList):
    patList[i] = (re.compile(pat[0]), pat[1])

for i, pat in enumerate(patListTable):
    patListTable[i] = (re.compile(pat[0]), pat[1])
    
for i, pat in enumerate(patListSection):
    patListSection[i] = (re.compile(pat[0]), pat[1])
