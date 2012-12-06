#-*-coding: utf-8 -*-

import pagegenerators, re, datetime, sys, catlib, userlib, category, time, os
import wikipedia as pywikibot
from pywikibot import i18n

# constant
PAGEMAIN = u"ผู้ใช้:Nullzerobot/บริการย้ายหมวดหมู่"
PAGEPENDING = u"ผู้ใช้:Nullzerobot/บริการย้ายหมวดหมู่/หมวดหมู่ที่รอการพิจารณา"
PAGEREPORT =  u"ผู้ใช้:Nullzerobot/รายงาน/บริการย้ายหมวดหมู่"
SIMULATE = False
VERIFYEDITCOUNT = 50
VERIFYTIME = 300000000
DONOTMOVE = False
FLUSHPENDING = u"-pending"
LOGPATH = "/home/nullzero/pywikipedia/logs/automovelog.txt"
# end constant

site = pywikibot.getSite()

def domove(source, dest):
    if DONOTMOVE: return None
    robot = category.CategoryMoveRobot(source, dest, batchMode=True,
editSummary=u"", inPlace=False, titleRegex=None, withHistory=False)
    robot.run()
    pageCat = pywikibot.Page(site, u"หมวดหมู่:" + source)
    pageCat.put(u"{{ลบ|บอตย้ายหมวดหมู่ไป[[:หมวดหมู่:" + dest + u"]] แล้ว}}", u"ย้ายหมวดหมู่โดยบอต")
    return None

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
    os.system("echo \"run at " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\" >> " + LOGPATH)
    flag = False
    pageprocess = None
    if (len(pywikibot.handleArgs(*args)) > 0) and (pywikibot.handleArgs(*args)[0] == FLUSHPENDING):
        flag = True
        pageprocess = PAGEPENDING
    else:
        pageprocess = PAGEMAIN

    argument = u"-log"
    if(SIMULATE): argument += u" -simulate"
    pywikibot.handleArgs(argument)
    pageMain = pywikibot.Page(site, pageprocess)
    text = pageMain.get(get_redirect = True)
    splitlist = text.split(u'-->')
    pre, post = splitlist
    pre += u'-->'
    text = post

    pattern = re.compile(u'\|(.*)\|\|.*\[\[:.*:(.*)\]\].*\[\[:.*:(.*)\]\].*\|\|(.*)\n.*\n')
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
        line = u""
        line += u"| "
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
            line += u"\n|-\n"
            report += line
        else:
            isPend = True
            line += u"\n|-\n"
            pending += line

    if (not isMove) and (not isPend): sys.exit()

    report += u"|}"
    pending += u"|}"

    summary = u"ดำเนินการย้ายหมวดหมู่ ณ เวลา "
    summary += datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pageMain.put(pre + text, u"ดำเนินการย้ายหมวดหมู่ ณ เวลา " + summary)

    if isMove:
        pageReport = pywikibot.Page(site, PAGEREPORT)
        text = pageReport.get(get_redirect = True)
        pattern = re.compile(u'\|\}')
        text = pattern.sub(u"", text, 1)
        text += report
        pageReport.put(text, summary)

    if isPend:
        pagePending = pywikibot.Page(site, PAGEPENDING)
        text = pagePending.get(get_redirect = True)
        pattern = re.compile(u'\|\}')
        text = pattern.sub(u"", text, 1)
        text += pending
        pagePending.put(text, summary)
    
    os.system("echo \"move at " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\" >> " + LOGPATH)
    pywikibot.stopme()

if __name__ == "__main__":
    try:
        lockfile = os.popen('ls automovecat.lock 2> /dev/null').read()
        if lockfile != "": sys.exit()
        os.system('echo > automovecat.lock')
        main()
    finally:
        pywikibot.stopme()
        os.system('rm automovecat.lock')
