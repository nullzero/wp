# -*- coding: utf-8 -*-

import sys, re, string, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try: from lib import preload
except:
    print "Cannot import preload. Exit!"
    sys.exit()

from lib import libdate
from lib.miscellaneous import remove_wikicode
import pagegenerators
import wikipedia as pywikibot

env = preload.env
site = pywikibot.getSite()

if __name__ == "__main__":
    pywikibot.handleArgs(u"-log")
    pywikibot.output(u"'veryshort-script' is invoked. (%s)" % libdate.getTime())
    site = pywikibot.getSite()
    
    genfac = pagegenerators.GeneratorFactory()
    generator = genfac.getCategoryGen(u':บทความที่มีเนื้อหาน้อยมาก', 0))
    
    for page in generator:
        pywikibot.output(u"I am checking " + page.title())
        original_content = page.get()
        content = remove_wikicode(original_content, space = True)
        
        if len(content) >= 1000:
            pywikibot.output(page.title())
            pat = re.compile(u"\{\{สั้นมาก\}\}\s*")
            original_content = pat.sub(u"", original_content)
            page.put(original_content, u"บทความมีความยาวพอควรแล้ว นำป้ายสั้นมากออก")
    
    pywikibot.output(u"'veryshort-script' terminated. (%s)" % libdate.getTime())
    pywikibot.stopme()
