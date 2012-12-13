# -*- coding: utf-8 -*-

from urllib import unquote

import re, sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try: from lib import preload
except:
    print "Cannot import preload. Exit!"
    sys.exit()

from lib import libdate    
import wikipedia as pywikibot

site = pywikibot.getSite()
pat = re.compile(u"http://\S+", re.DOTALL)

def doPage(page):
    pywikibot.output(u"Process %s" % page.title())
    original_content = page.get()
    content = pat.sub(lambda s: unquote(s.group().encode("utf-8")).decode("utf-8").replace(u'"', u'%22'), 
        original_content)
    if content == original_content:
        pywikibot.output(u"Nothing to do here!")
    else:
        pywikibot.output(u"Change %s" % page.title())
        page.put(content, u"แก้ url โดยบอต")

if __name__ == "__main__":
    pywikibot.handleArgs(u"-log")
    pywikibot.output(u"'decode-script' is invoked. (%s)" % libdate.getTime())
    page = pywikibot.Page(site, u"ความผิดต่อองค์พระมหากษัตริย์ไทย")
    doPage(page)
    pywikibot.output(u"'decode-script' terminated. (%s)" % libdate.getTime())
    pywikibot.stopme()
