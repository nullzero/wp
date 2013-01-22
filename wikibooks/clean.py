# -*- coding: utf-8 -*-

import sys, os, re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try: from lib import preload
except:
    print "เรียกใช้ไลบรารีไม่ได้ จบการทำงาน!"
    sys.exit()

import wikipedia as pywikibot
pywikibot.handleArgs("-family:wikibooks")
import pagegenerators, movepages
import re

from lib import libcleaner

#gen = pagegenerators.AllpagesPageGenerator()
mainName = u"กิมป์/tools"
nameCat = u"กิมป์"
site = pywikibot.getSite()
gen = pagegenerators.LinkedPageGenerator(pywikibot.Page(site, mainName))
categorizeEnable = True

always = False

def categorize(name, content):
    content = re.sub(u'\[\[หมวดหมู่:.*', u'', content, flags = re.DOTALL)
    content = re.sub(u'$(?!\n)', u'\n[[หมวดหมู่:%s]]' % name, content)
    return content

def main():
    global always
    for page in gen:
        if page.title().startswith(u"/"): page = pywikibot.Page(site, mainName + page.title())
        try: ocontent = page.get()
        except: continue
        
        print ">>>", page.title()
        
        content = ocontent
        if (re.search(u'<\s*/?\s*(tr|td)\s*>', content) is not None) or \
            (re.search(u'<\s*/?\s*(source)\s*>', content) is not None): continue
        content = re.sub(u'<\s*font.*?color.*?#ffffff.*?>.*?<\s*/\s*font\s*>', u'\n', content)
        content = re.sub(u'<\s*font.*?>(.*?)<\s*/\s*font\s*>', u'\g<1>', content)
        content = re.sub(u'<\s*p\s*>(.*?)<\s*/\s*p\s*>', u'\n\g<1>\n', content, re.DOTALL)
        content = re.sub(u'<\s*/\s*p\s*>', u'', content)
        content = re.sub(u'^[ \t\r\f\v]+', u'', content, flags = re.MULTILINE)
        if categorizeEnable: content = categorize(nameCat, content)
        content = re.sub(u'^\d+\.', u'#', content, flags = re.MULTILINE)
        content = re.sub(u'<\s*br\s*/?\s*>\s*?$', u'\n\n', content, flags = re.MULTILINE)
        content = re.sub(u'^\*(.*?)$\s*^(?=\*)', u'*\g<1>\n', content, flags = re.MULTILINE)
        content = re.sub(u'^#(.*?)$\s*^(?=#)', u'#\g<1>\n', content, flags = re.MULTILINE)
        content = re.sub(u'(\n[\ \t\r\f\v]*){3,}', u'\n\n\n', content, flags = re.MULTILINE)
        content = libcleaner.clean(content)
        
        if content != ocontent:
            pywikibot.showDiff(ocontent, content)
            if not always: choice = raw_input("proceed? : ")
            if (choice == 'n') or (choice == 'N'): continue
            if choice == 'a':
                always = True
                
            try:
                if categorizeEnable: page.put(content, u"โรบอต: จัดหมวดหมู่", force = True)
                else: page.put(content, u"โรบอต: เก็บกวาด", force = True)
            except:
                pass

if __name__ == "__main__":
    main()
