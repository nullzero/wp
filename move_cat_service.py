#-*-coding: utf-8 -*-

try: import utility
except: pass

import pagegenerators, re, datetime, sys, catlib, userlib, category, time, os, traceback
import wikipedia as pywikibot

env = utility.env

# constant
USER = u"ผู้ใช้:Nullzerobot"
PAGEMAIN = USER + u"/บริการย้ายหมวดหมู่"
PAGEPENDING = USER + u"/บริการย้ายหมวดหมู่/หมวดหมู่ที่รอการพิจารณา"
PAGEREPORT = USER + u"/บริการย้ายหมวดหมู่/กระบะทราย"
#PAGEREPORT =  USER + u"/รายงาน/บริการย้ายหมวดหมู่"
SIMULATE = False
VERIFYEDITCOUNT = 50
VERIFYTIME = 300000000
DONOTMOVE = False
FLUSHPENDING = u"-pending"
LOCKFILE = "movecat.lock"
SUFFIX = u"\n|}\n\n{{ผู้ใช้:Nullzerobot/บริการย้ายหมวดหมู่/หมวดหมู่ที่รอการพิจารณา}}"
# end constant

site = pywikibot.getSite()

def domove(source, dest):
    pywikibot.output(u"move from " + source + " to " + dest)
    if DONOTMOVE: return
    robot = category.CategoryMoveRobot(source, dest, batchMode=True,
        editSummary=u"", inPlace=False, titleRegex=None, withHistory=False)
    robot.run()
    pageCat = pywikibot.Page(site, u"หมวดหมู่:" + source)
    pageCat.put(u"{{ลบ|บอตย้ายหมวดหมู่ไป[[:หมวดหมู่:" + dest + u"]] แล้ว}}", u"ย้ายหมวดหมู่โดยบอต")

def verify(name, flag):
    if(flag): return True
    if name == u"N/A": return False
    pattern = re.compile(u'\{\{.*\|(.*)\}\}')
    result = pattern.match(name)
    if not result: return False
    name = result.group(1)
    user = userlib.User(site, name)
    if not user.isRegistered(): return False
    if user.editCount() < VERIFYEDITCOUNT: return False
    if user.isBlocked(): return False
    difftime = int(time.strftime('%Y%m%d%H%M%S', time.gmtime()))
    difftime -=  int(user.registrationTime())
    if(difftime < VERIFYTIME): return False
    return True

def catempty(title, flag):
    if(flag): return True
    cat = catlib.Category(site, 'Category:' + title)
    listOfArticles = cat.articlesList(recurse = False)
    return len(listOfArticles) == 0

def main(*args):
    pywikibot.output(u"Move-category service is invoked. (%s)" % 
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
    flag = False
    pageprocess = None
    if (len(pywikibot.handleArgs(*args)) > 0) and (pywikibot.handleArgs(*args)[0] == FLUSHPENDING):
        flag = True
        pageprocess = PAGEPENDING
    else:
        pageprocess = PAGEMAIN
    
    summary = u"ย้ายหมวดหมู่ ณ เวลา "
    summary += datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    pageMain = pywikibot.Page(site, pageprocess)
    text = pageMain.get(get_redirect = True)
    pre, post = text.split(u"-->")
    pre += u"-->" + SUFFIX
    
    if pre == text:
        pywikibot.output("Nothing to do here")
        return
        
    pageMain.put(pre, u"เริ่ม" + summary)
    
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
            line += datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
        pywikibot.output("Nothing to do here")
        return

    report += u"|}"
    pending += u"|}"

    if isMove:
        pageReport = pywikibot.Page(site, PAGEREPORT)
        text = pageReport.get(get_redirect = True)
        pattern = re.compile(u"\|\}")
        text = pattern.sub(u"", text, 1)
        text += report
        pageReport.put(text, summary)

    if isPend:
        pagePending = pywikibot.Page(site, PAGEPENDING)
        text = pagePending.get(get_redirect = True)
        pattern = re.compile(u"\|\}")
        text = pattern.sub(u"", text, 1)
        text += pending
        pagePending.put(text, summary)
        
    pywikibot.output(u"Moved categories. (%s)" % 
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    argument = u"-log"
    if(SIMULATE): argument += u" -simulate"
    pywikibot.handleArgs(argument)
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
        
    try: os.remove(lockfile)
    except: pywikibot.output(u"Can't remove lockfile.")
    pywikibot.output(u"Bye")
    pywikibot.stopme()
