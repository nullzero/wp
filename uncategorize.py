# -*- coding: utf-8  -*-

import utility
import subprocess, shlex, os
import wikipedia as pywikibot

pywikibot.handleArgs(u"-log")

pywikibot.output(u"'Uncategorize' is invoked. (%s)" % 
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

env = utility.env

prefix = shlex.split('python ' + os.path.join(env['WORKPATH'], 'pywikipedia/replace.py -always -regex'))
suffix = shlex.split(' -subcats:หน้าที่ยังไม่ได้จัดหมวดหมู่ "\[\[(Category|category):" "[[หมวดหมู่:"')
process = subprocess.call(prefix + suffix)
suffix = shlex.split(' -cat:หน้าที่ยังไม่ได้จัดหมวดหมู่ "\[\[(Category|category):" "[[หมวดหมู่:"')
process = subprocess.call(prefix + suffix)
suffix = shlex.split('-subcats:หน้าที่ยังไม่ได้จัดหมวดหมู่ -requiretext:"\[\[หมวดหมู่:" "\{\{ต้องการหมวดหมู่\}\}" ""')
process = subprocess.call(prefix + suffix)
suffix = shlex.split('-cat:หน้าที่ยังไม่ได้จัดหมวดหมู่ -requiretext:"\[\[หมวดหมู่:" "\{\{ต้องการหมวดหมู่\}\}" ""')
process = subprocess.call(prefix + suffix)

pywikibot.output(u"'Uncategorize' terminated. (%s)" % 
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
