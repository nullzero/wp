# -*- coding: utf-8 -*-

import re, sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try: from lib import preload
except:
    print "Cannot import preload. Exit!"
    sys.exit()

import wikipedia as pywikibot
import pagegenerators
import re

site = pywikibot.getSite()
for page in site.allpages(start='รายชื่อเพย์-เพอร์-วิวของทีเอ็นเอ', namespace=0, includeredirects=False):
    print "check", page.title()
    try: content = page.get()
    except: continue
    reflist = re.findall("<\s*ref\s*>(.*?)<\s*/\s*ref\s*>", content, re.DOTALL)
    for ref in reflist:
        if re.search("wikipedia\.org", ref) is not None:
            with open("fileref.txt", "a") as f:
                f.write(page.title().encode("utf-8") + '\n')
            print ">>>", page.title()
            break
