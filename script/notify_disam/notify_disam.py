# -*- coding: utf-8 -*-

DEBUG = False

import sys, os, re, time, traceback, urllib, subprocess
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try: from lib import preload_notify
except:
    print "เรียกใช้ไลบรารีไม่ได้ จบการทำงาน!"
    sys.exit()

import query, userlib
from lib import libdate, liblang, libstring, libgenerator, librevision, miscellaneous
import wikipedia as pywikibot

pywikibot.handleArgs(u"-user:nullzerotest")

startChecking = 1
site = pywikibot.getSite()
env = preload_notify.env
insertDisamT = pywikibot.Page(site, u"User:Nullzerobot/ข้อความ/insert-disam").get()

revertedDict = {}

def notify(user, page, link):
    if user == u"JBot": return
    usertalk = pywikibot.Page(site, u"User talk:" + user)
    if not usertalk.exists(): pywikibot.output(u">>> ไม่มีหน้านี้มาก่อน - ไอพี ไม่เตือน")
    content = usertalk.get()
    listold = re.findall(u"<!-- เริ่มลิงก์ -->(.*?)<!-- จบลิงก์ -->", content)
    for linkold in listold:
        if linkold == link:
            pywikibot.output(u">>> แต่เคยแจ้งแล้ว เลิกการแจ้ง!")
            return
    
    message = insertDisamT
    message = message.replace(u"<!-- ชื่อผู้ใช้ -->", user)
    message = message.replace(u"<!-- หน้า -->", page)
    message = message.replace(u"<!-- ลิงก์ -->", link)
    
    try:
        usertalk.put(content + u"\n" + message + u" --~~~~", u"แจ้งใส่ลิงก์โยงไปยังหน้าแก้กำกวม")
    except:
        pywikibot.output(traceback.format_exc().decode("utf-8"))
        return
        
    pywikibot.output(u">>> เรียบร้อย!")

def check(revision):
    newpage = False
    try:
        page = librevision.getRevision(revision[1]['revid'], 'diff')
    except:
        pywikibot.output(traceback.format_exc().decode("utf-8"))
        return
        
    if DEBUG and (page['title'] != env['SANDBOX'].decode("utf-8")): return
    
    pywikibot.output(u"=== กำลังตรวจสอบหน้า %s @ %s โดย %s" % (page['title'], page['revisions'][0]['timestamp'], page['revisions'][0]['user']))
    
    """
    ยกเลิกการตรวจสอบ: ผิดพลาด
    """
    try:
        curpage = pywikibot.Page(site, page['title'])
        content = curpage.get()
    except:
        pywikibot.output(u"!!! ไม่สามารถเรียกข้อมูลหน้าได้ ยกเลิกการตรวจสอบ")
        pywikibot.output(traceback.format_exc().decode("utf-8"))
        return
    
    if not page['revisions'][0]['diff']['from']:
        pywikibot.output(u"หน้านี้เป็นหน้าใหม่!")
        newpage = True
        change = librevision.getRevision(revision[1]['revid'], 'content')
    else:
        change = page['revisions'][0]['diff']['*']
    
    lines = change.splitlines()
    addedLine = u""
    
    for line in lines:
        line = line.strip()
        if line.startswith(u'<td class="diff-addedline">') or newpage:
            if not newpage:
                line = re.sub(u"<td.*?>", u"", line)
                line = re.sub(u"</td>", u"", line)
                line = re.sub(u"<div>", u"", line)
                line = re.sub(u"</div>", u"", line)
                line = re.sub(u"<span.*?>", u"", line)
                line = re.sub(u"</span>", u"", line)
                line = re.sub(u"&lt;", u"<", line)
                line = re.sub(u"&gt;", u">", line)
            
            addedLine += line.rstrip() + u"\n"
    
    links = re.findall(u"\[\[(.*?)(\|.*?)?\]\]", addedLine)
    
    disamlinks = []
    
    for link in links:
        if u":" in link[0]: continue
        if link[0].startswith(u"#"): continue
        try:
            if pywikibot.Page(site, link[0]).isDisambig():
                disamlinks.append(link[0])
        except: pywikibot.output(traceback.format_exc().decode("utf-8"))
    
    if len(disamlinks) != 0:
        pywikibot.output(u">>> พบลิงก์แก้กำกวม")
        notify(page['revisions'][0]['user'], page['title'], u"* [[" + u"]]\n* [[".join(disamlinks) + u"]]")
    
if __name__ == "__main__":
    pywikibot.handleArgs("-log")
    pywikibot.output(u"สคริปต์แจ้งโยงไปยังหน้าแก้กำกวมเริ่มทำงาน ณ เวลา %s" % libdate.getTime())
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "-d": DEBUG = True
        
    gen = libgenerator.recentchanges(number = startChecking, namespace = "|".join([str(x) for x in xrange(0, 16, 2) if x != 2]), repeat = True)
    
    try:
        for revision in gen: check(revision)
    except:
        preload_notify.error()
    
    pywikibot.output(u"สคริปต์แจ้งโยงไปยังหน้าแก้กำกวมหยุดทำงาน ณ เวลา %s" % libdate.getTime())
    pywikibot.stopme()
