# -*- coding: utf-8 -*-

import datetime, subprocess, shlex, os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try: from lib import preload
except:
    print "Cannot import preload. Exit!"
    sys.exit()

from lib import libdate
import wikipedia as pywikibot

env = preload.env

if __name__ == "__main__":
    pywikibot.handleArgs(u"-log")
    pywikibot.output(u"'uncategorize-script' is invoked. (%s)" % libdate.getTime())

    prefix = shlex.split("python " + os.path.join(env['WORKPATH'], "pywikipedia/replace.py -always -regex"))
    suffix = shlex.split(' -subcats:หน้าที่ยังไม่ได้จัดหมวดหมู่ "\[\[(Category|category):" "[[หมวดหมู่:"')
    process = subprocess.call(prefix + suffix)
    suffix = shlex.split(' -cat:หน้าที่ยังไม่ได้จัดหมวดหมู่ "\[\[(Category|category):" "[[หมวดหมู่:"')
    process = subprocess.call(prefix + suffix)
    suffix = shlex.split('-subcats:หน้าที่ยังไม่ได้จัดหมวดหมู่ -requiretext:"\[\[หมวดหมู่:" "\{\{ต้องการหมวดหมู่\}\}" ""')
    process = subprocess.call(prefix + suffix)
    suffix = shlex.split('-cat:หน้าที่ยังไม่ได้จัดหมวดหมู่ -requiretext:"\[\[หมวดหมู่:" "\{\{ต้องการหมวดหมู่\}\}" ""')
    subprocess.call(prefix + suffix)

    pywikibot.output(u"'uncategorize-script' terminated. (%s)" % libdate.getTime())
    pywikibot.stopme()
