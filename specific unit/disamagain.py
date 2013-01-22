# -*- coding: utf-8 -*-

DEBUG = False

import sys, os, re, time, traceback, urllib, subprocess
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try: from lib import preload
except:
    print "เรียกใช้ไลบรารีไม่ได้ จบการทำงาน!"
    sys.exit()

import query, userlib
from lib import libdate, liblang, libstring, libgenerator, librevision, miscellaneous
import wikipedia as pywikibot

def main():
    gen = libgenerator.CatGenerator(u"การแก้ความกำกวม")
    for page in gen:
        print "กำลังตรวจสอบ", page.title()
        if page.namespace() != 0: continue
        try:
            ocontent = page.get()
            if re.search(u"\{\{\s*(แก้ความกำกวม|คำกำกวม|แก้กำกวม|Disambig)\s*\}\}", ocontent, flags = re.IGNORECASE) is None:
                print "... พบหน้าแก้กำกวมมีปัญหา"
                content = ocontent
                content = re.sub(u"\[\[\s*(หมวดหมู่|category):การแก้ความกำกวม\s*\]\]", u"", content, flags = re.IGNORECASE)
                if content != ocontent:
                    content += u"\n{{แก้ความกำกวม}}"
                    page.put(content, u"เปลี่ยนมาใช้แม่แบบแก้ความกำกวมแทน")
                    print ">>> เรียบร้อย"
                else:
                    print ">>> ผิดพลาด!"
                    with open("log-disam.txt", "a") as f:
                        f.write(page.title().encode("utf-8") + "\n")
        except:
            pywikibot.output(traceback.format_exc().decode("utf-8"))
    
if __name__ == "__main__":
    try:
        main()
    except:
        pywikibot.output(traceback.format_exc().decode("utf-8"))
        
    pywikibot.stopme()
