# -*- coding: utf-8 -*-

import re, sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try: from lib import preload
except:
    print "Cannot import preload. Exit!"
    sys.exit()

from lib import libgenerator
import wikipedia as pywikibot
import pagegenerators, query
import re

site = pywikibot.getSite()

params = {
    'action'    : 'query',
    'list'      : 'querypage',
    'qppage'     : 'Uncategorizedpages',
    'qplimit' : 5000
}
data = query.GetData(params)[u'query'][u'querypage'][u'results']

for page in data:
    pageobj = pywikibot.Page(site, page['title'])
    content = pageobj.get()
    if re.search(u"\{\{\s*(แก้ความกำกวม|คำกำกวม|แก้กำกวม|Disambig)\s*\}\}", content) is not None:
        pageobj.put(content)

"""
for page in gen:
    print "check", page.title()
    
    
    
    
    if re.search(u"\{\{\s*(แก้ความกำกวม|คำกำกวม|แก้กำกวม|Disambig)\s*\}\}", content, re.IGNORECASE) is None:
        with open("filedisam.txt", "a") as f:
                f.write(page.title().encode("utf-8") + '\n')
        print ">>>", page.title()
    else:
        page.put(content)
"""
