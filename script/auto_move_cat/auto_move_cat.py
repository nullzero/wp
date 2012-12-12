# -*- coding: utf-8 -*-

import re, sys, time, os, traceback
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try: from lib import preload
except:
    print "Cannot import preload. Exit!"
    sys.exit()

from lib import libdate
import wikipedia as pywikibot
import pagegenerators, catlib, userlib, category

env = preload.env

# constant
USER = u"ผู้ใช้:Nullzerobot"
PAGEMAIN = USER + u"/บริการย้ายหมวดหมู่"
PAGEPENDING = USER + u"/บริการย้ายหมวดหมู่/หมวดหมู่ที่รอการพิจารณา"
PAGEREPORT =  USER + u"/รายงาน/บริการย้ายหมวดหมู่"
SIMULATE = False
VERIFYEDITCOUNT = 50
VERIFYTIME = 300000000
DONOTMOVE = False
FLUSHPENDING = "-pending"
LOCKFILE = "movecat.lock"
SUFFIX = u"\n|}\n\n{{/หมวดหมู่ที่รอการพิจารณา}}"
# end constant

site = pywikibot.getSite()

def domove(source, dest):
    pywikibot.output(u"move from " + source + " to " + dest)
    if DONOTMOVE: return
    robot = category.CategoryMoveRobot(source, dest, batchMode = True,
        editSummary = u"", inPlace = False, titleRegex = None, withHistory = False)
    robot.run()
    pageCat = pywikibot.Page(site, u"หมวดหมู่:" + source)
    pageCat.put(u"{{ลบ|บอตย้ายหมวดหมู่ไป[[:หมวดหมู่:" + dest + u"]] แล้ว}}", u"ย้ายหมวดหมู่โดยบอต")

def verify(name, flag):
    if(flag): return True
    if name == u"N/A": return False
    pattern = re.compile(u"\{\{.*\|(.*)\}\}")
    result = pattern.match(name)
    if not result: return False
    name = result.group(1)
    user = userlib.User(site, name)
    if not user.isRegistered(): return False
    if user.editCount() < VERIFYEDITCOUNT: return False
    if user.isBlocked(): return False
    difftime = int(time.strftime("%Y%m%d%H%M%S", time.gmtime()))
    difftime -=  int(user.registrationTime())
    if(difftime < VERIFYTIME): return False
    return True

def catempty(title, flag):
    if(flag): return True
    cat = catlib.Category(site, 'Category:' + title)
    listOfArticles = cat.articlesList(recurse = False)
    return len(listOfArticles) == 0

def main(*args):
    pywikibot.output(u"'move-category service' is invoked. (%s)" % libdate.getTime())
        
    flag = False
    
    if (len(pywikibot.handleArgs(*args)) > 0) and (pywikibot.handleArgs(*args)[0] == FLUSHPENDING):
        pywikibot.output(u"Pending mode")
        flag = True
        pageprocess = PAGEPENDING
    else:
        pageprocess = PAGEMAIN
    
    pageMain = pywikibot.Page(site, pageprocess)
    text = pageMain.get(get_redirect = True)
    pre, post = text.split(u"-->")
    
    if SUFFIX.strip() == post.strip():
        pywikibot.output("Nothing to do here")
        return
    
    summary = u"ย้ายหมวดหมู่ ณ เวลา "    
    pageMain.put(pre + u"-->" + SUFFIX, u"เริ่ม" + summary + libdate.getTime())
    
    text = post

    pattern = re.compile(u"\|-.*\n\|(.*)\|\|.*\[\[:.*:(.*)\]\].*\[\[:.*:(.*)\]\].*\|\|(.*)\n")
    report = u""
    pending = u""
    isMove = False
    isPend = False
    
    while True:
        result = pattern.search(text)
        if not result: break
        vdate = result.group(1).strip()
        vfrom = result.group(2).strip()
        vto   = result.group(3).strip()
        vby   = result.group(4).strip()
        text = pattern.sub(u"", text, 1)
        if(not vby): vby = u"N/A"
        
        line = u"|-\n| "
        line += vdate
        line += u" || [[:หมวดหมู่:" 
        line += vfrom 
        line += u"]] || [[:หมวดหมู่:"
        line += vto
        line += u"]] || "
        line += vby

        if vdate and vfrom and vto and verify(vby, flag) and catempty(vto, flag):
            isMove = True
            domove(vfrom, vto)
            line += u" || "
            line += libdate.getTime()
            line += u"\n"
            report += line
        else:
            isPend = True
            line += u"\n"
            pending += line

    text = text.strip()[:-len(SUFFIX)]
    
    if text != u"":
        pywikibot.output("Error!")
        pywikibot.output(text)
    
    if (not isMove) and (not isPend):
        pywikibot.output("Nothing to do here (WTF)")
        return

    report += u"|}"
    pending += u"|}"
    p_end = re.compile(u"\|\}")
    
    if isMove:
        pageReport = pywikibot.Page(site, PAGEREPORT)
        text = pageReport.get(get_redirect = True)
        text = p_end.sub(u"", text, 1)
        text += report
        pageReport.put(text, summary + libdate.getTime())

    if isPend:
        pagePending = pywikibot.Page(site, PAGEPENDING)
        text = pagePending.get(get_redirect = True)
        text = p_end.sub(u"", text, 1)
        text += pending
        pagePending.put(text, summary + libdate.getTime())
        
    pywikibot.output(u"'move-category service' terminated. (%s)" % libdate.getTime())

if __name__ == "__main__":
    pywikibot.handleArgs("-log")
    if(SIMULATE): pywikibot.handleArgs("-simulate")
    lockfile = os.path.join(env['TMP'], LOCKFILE)
    
    if os.path.exists(lockfile):
        pywikibot.output(u"This script is locked.")
        pywikibot.stopme()
        sys.exit()
    
    open(lockfile, 'w').close() 
    
    try:
        main()
    except:
        var = traceback.format_exc()
        pywikibot.output(u"Unexpected error!")
        pywikibot.output(var.encode("utf-8"))
        sys.exit()
        
    try: os.remove(lockfile)
    except: pywikibot.output(u"Can't remove lockfile.")
    pywikibot.output(u"Bye")
    pywikibot.stopme()
