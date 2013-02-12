# -*- coding: utf-8 -*-

from dateutil import relativedelta
from datetime import datetime
import re, sys, os, difflib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try: from lib import preload
except:
    print "Cannot import preload. Exit!"
    sys.exit()

import wikipedia as pywikibot
import pagegenerators

site = preload.site
    
gen = pagegenerators.ReferringPageGenerator(pywikibot.Page(site, u"แม่แบบ:เพิ่งตาย"), onlyTemplateInclusion = True)

pat = re.compile(ur"(?i)\{\{\s*(เพิ่งตาย|เพิ่งสิ้นพระชนม์|Recent death)\s*\}\}\s*")

for page in gen:
    print ">>>", page.title()
    history = page.getVersionHistory()
    oldversion = page.getOldVersion(history[0][0])
    doerase = False
    found = False
    for cntversion, version in enumerate(history):
        if cntversion == 0: continue
        newversion = oldversion
        oldversion = page.getOldVersion(version[0])
        dobj = difflib.SequenceMatcher(a = oldversion, b = newversion)
        print "oldversion =", version[0]
        for t in dobj.get_opcodes():
            if t[0] == "insert":
                if pat.search(newversion[t[3]:t[4]]) is not None:
                    found = True
                    dateadded = datetime.strptime(str(history[cntversion - 1][1]), '%Y-%m-%dT%H:%M:%SZ')
                    datenow = datetime.today()
                    dat = relativedelta.relativedelta(datenow, dateadded)
                    print dat
                    if dat.days > 15 or dat.month > 0 or dat.year > 0: doerase = True
                    break
        if found: break
    if doerase:
        page.put(pat.sub("", page.get()), u"ลบแม่แบบเพิ่งตายออก")

pywikibot.stopme()
