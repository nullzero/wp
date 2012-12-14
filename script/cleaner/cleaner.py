# -*- coding: utf-8 -*-

import urllib

import re, sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try: from lib import preload
except:
    print "Cannot import preload. Exit!"
    sys.exit()

from lib import libdate    
import wikipedia as pywikibot
'''
site = pywikibot.getSite()
pat = re.compile(u"https?://\S+", re.DOTALL)

def doPage(page):
    pywikibot.output(u"Process %s" % page.title())
    original_content = page.get()
    
    print pat.search(original_content).group()
    
    """
    content = pat.sub(lambda s: unquote(s.group().encode("utf-8")).decode("utf-8"
        ).replace(u'"', u'%22').replace(u' ', u'%20').replace(u'<', u'%3C').replace(u'>', 
        u'%3E').replace(u'[', u'%5B').replace(u'[', u'%5D') + call(s.group()), original_content)"""
        
    
    #print content, unquote(original_content.encode("utf-8"))
    if content == original_content:
        pywikibot.output(u"Nothing to do here!")
    else:
        pywikibot.output(u"Change %s" % page.title())
        page.put(content, u"แก้ url โดยบอต")

if __name__ == "__main__":
    pywikibot.handleArgs(u"-log")
    pywikibot.output(u"'decode-script' is invoked. (%s)" % libdate.getTime())
    page = pywikibot.Page(site, u"ผู้ใช้:Nullzero/กระบะทราย")
    doPage(page)
    pywikibot.output(u"'decode-script' terminated. (%s)" % libdate.getTime())
    pywikibot.stopme()
'''

pat = re.compile('(ftp|https?)://[\w/.,;:@&=%#\\\?_!~*\'|()\"+-]+', re.DOTALL)
mystr = "https://www.google.com/search?q=%26%E0%B8%89%E0%B8%B1%E0%B8%99</ref>"
print pat.sub(lambda s: urllib.unquote(s.group()), mystr)
