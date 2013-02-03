# -*- coding: utf-8 -*-

import sys, re, string, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try: from lib import preload
except:
    print "เรียกใช้ไลบรารีไม่ได้ จบการทำงาน!"
    sys.exit()

from lib import libdate, libgenerator, miscellaneous
import pagegenerators
import wikipedia as pywikibot

env = preload.env
site = pywikibot.getSite()

if __name__ == "__main__":
    pywikibot.handleArgs(u"-log")
    pywikibot.output(u"สคริปต์ลบป้ายสั้นมากเริ่มทำงาน ณ เวลา %s" % libdate.getTime())
    site = pywikibot.getSite()
    
    generator = libgenerator.CatGenerator(u'บทความที่มีเนื้อหาน้อยมาก')
    
    for page in generator:
        original_content = page.get(get_redirect = True)
        content = original_content
        content = pywikibot.removeCategoryLinks(content)
        content = pywikibot.removeLanguageLinks(content)
        content = re.sub(u"\s+", u" ", content)
        while True:
            newcontent = re.sub("\{\{(?:(?!\{\{|\}\}).)*\}\}", u"", content, flags = re.DOTALL)
            if content == newcontent: break
            content = newcontent
        content = re.sub("\{\|.*?\|\}", u"", content, flags = re.DOTALL)
        content = re.sub("<ref.*?</ref>", u"", content, flags = re.DOTALL)
        content = re.sub("(?<!\[)\[(?!\[).*?\]", u"", content, flags = re.DOTALL)
        pywikibot.output(u"%s : %d" % (page.title(), len(content)))
        if len(content) >= 1000:
            pywikibot.output(u">>> ยาวแล้ว")
            content = original_content.replace(u"{{สั้นมาก}}", u"")
            if content != original_content:
                page.put(content, u"บทความมีความยาวพอควรแล้ว นำป้ายสั้นมากออก")
    
    pywikibot.output(u"สคริปต์ย้อนก่อกวนหยุดทำงาน ณ เวลา %s" % libdate.getTime())
    pywikibot.stopme()
