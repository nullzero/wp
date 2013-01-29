# -*- coding: utf-8  -*-

import sys

sys.path.append("/home/sorawee/wp")

from lib import preload
from lib import libcleaner, liblang
import wikipedia as pywikibot

site = preload.site
always = False
for page in site.allpages(start='ISO', includeredirects = False):
    print ">>>", page.title()
    try:
        ocontent = page.get()
    except:
        preload.error()
        continue
    content = ocontent
    content = liblang.fixRepetedVowel(content)
    content = libcleaner.clean(content)
    
    if content != ocontent:
        pywikibot.showDiff(ocontent, content)
        if not always:
            r = raw_input("p: ")
            if r == 'n': continue
            elif r == 'a': always = True
            
        try: page.put(content, u"เก็บกวาด")
        except: preload.error()
