# -*- coding: utf-8 -*-

import sys, os, re, time, traceback
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try: from lib import preload
except:
    print "เรียกใช้ไลบรารีไม่ได้ จบการทำงาน!"
    sys.exit()

import query, userlib
from lib import libdate, liblang, libstring, libgenerator, librevision, miscellaneous
import wikipedia as pywikibot

startChecking = 10
site = preload.site

def isSpam(pageName, revision, user):
    contribs = librevision.allContribute(pageName)
    cnt = 0
    startOp = False
    for i in contribs:
        if startOp and user == i['user']: cnt += 1
        if i['revid'] == revision: startOp = True
    
    pywikibot.output(u"เค้าคนนี้แก้หน้านี้มาแล้ว %s ครั้ง" % cnt)
    return cnt < 3

revertedDict = {}

import subprocess

def notifyOSD(s):
    try: subprocess.call(["notify-send", s.encode("utf-8")])
    except: pass

def revert(page, reason, newpage, template = None, makeWar = False):
    summary = (u"ลบ" if newpage else u"ย้อน") + u"บทความ" + reason
    pywikibot.output(page['title'] + u": " + summary)
    notifyOSD(page['title'] + u": " + summary)
    
    if not makeWar:
        if page['title'] in revertedDict:
            if revertedDict[page['title']] == 0:
                pywikibot.output(u"อย่ามีสงครามกันเลย!")
                return
            revertedDict[page['title']] += 1
        else:
            revertedDict[page['title']] = 0
    
    if newpage:
        pageObject = pywikibot.Page(site, page['title'])
        if int(page['ns']) % 2 == 1:
            try: pageObject.put(u"{{อธิบายหน้าพูดคุย}}", summary + preload.summarySuffix, botflag = False, force = True)
            except: preload.error()
        else:
            try: pageObject.put(u"{{ลบ|" + summary + "}}\n" + pageObject.get(), summary + preload.summarySuffix, botflag = False, force = True)
            except: preload.error()
        return
    
    librevision.revert(page['pageid'], page['revisions'][0]['revid'], summary, page['title'])

const = {
    'UNLIM' : -1,
}

NotEncyList = [
    ([u"==\s*วิสัยทัศน์\s*==", u"==\s*พันธกิจ\s*=="], u"วิสัยทัศน์ฯ ไม่เป็นสาราฯ", const['UNLIM']), 
]

try:
    VandalBlacklist = []
    UserBlacklist = []
    
    with open(preload.File(__file__, "VandalBlacklist.txt")) as f:
        lines = f.read()
        for line in lines:
            dat = line.decode("utf-8").strip()
            if dat != u"": VandalBlacklist.append(dat)
        
    with open(preload.File(__file__, "UserBlacklist.txt")) as f:
        lines = f.read()
        for line in lines:
            dat = line.decode("utf-8").strip()
            if dat != u"": UserBlacklist.append(dat)
            
except:
    preload.error()

def clean(page):
    if page is None: return
    liblang.fixRepetedVowel(page)

def check(revision):
    """
    มาดูกันก่อนเลย ก่อกวนหรือไม่!
    """
    newpage = False
    page = librevision.getRevision(revision[1]['revid'], 'diff')
    pywikibot.output(u"กำลังตรวจสอบหน้า " + page['title'] + u" @ " + page['revisions'][0]['timestamp'])
    
    """
    ยกเลิกการตรวจสอบ: ผิดพลาด
    """
    try:
        curpage = pywikibot.Page(site, page['title'])
        content = curpage.get()
    except:
        pywikibot.output(u"ผิดพลาด: ไม่สามารถเรียกข้อมูลหน้าได้ ยกเลิกการตรวจสอบ")
        pywikibot.output(traceback.format_exc().decode("utf-8"))
        return
        
    """
    ยกเว้นทุกอย่างให้ sysop
    """
    user = userlib.User(site, page['revisions'][0]['user'])
    if user.isRegistered() and ('sysop' in user.groups()):
        return curpage
        
    autoconfirmed = user.isRegistered() and ('autoconfirmed' in user.groups())
    
    """
    ยกเลิกการตรวจสอบ: ไฟล์ของผู้ใช้
    TODO: หวังว่าคงไม่เจอสแปมในหน้านี้นะ
    """
    if page['title'].endswith(u".js") or page['title'].endswith(u".css"):
        pywikibot.output("พบไฟล์ผู้ใช้! ยกเลิกการตรวจสอบ")
        return
    
    """
    ยกเลิกการตรวจสอบ: หน้าทดลองเขียน
    TODO: หวังว่าคงไม่เจอสแปมในหน้านี้นะ
    """
    if (page['title'].startswith(u"ผู้ใช้:" + page['revisions'][0]['user']) and \
        (re.search(u"(ทดลองเขียน|กระบะทราย|กระดาษทด)", page['title']) is not None)) \
        or (re.sub("\ ", "_", page['title']) in miscellaneous.sandboxPages):
        pywikibot.output(u"พบหน้าทดลอง! ยกเลิกการตรวจสอบ")
        return
            
    if not page['revisions'][0]['diff']['from']:
        pywikibot.output(u"หน้านี้เป็นหน้าใหม่!")
        newpage = True
        change = librevision.getRevision(revision[1]['revid'], 'content')
    else:
        change = page['revisions'][0]['diff']['*']
    
    """
    ยกเลิกการตรวจสอบ: มีป้ายแล้ว
    """
    if re.search(u"\{\{(ลบ|Delete|Sd|ละเมิดลิขสิทธิ์|Copyvio).*?\}\}", content, re.IGNORECASE | re.DOTALL):
        pywikibot.output(u"มีป้ายติดอยู่แล้ว! ยกเลิกการตรวจสอบ")
        return
    
    """
    ก่อกวนหรือไม่เป็นสารานุกรม เพราะ ความยาวสั้นจัด
    1. ยกเว้น autoconfirmed
    2. ไม่ใช่ ns:main เพราะอาจจะเจอพวก {{ดูเพิ่ม}} ใน ns:cat หรือ ns:template ที่สั้นจัด
    3. ตรวจหน้าพูดคุย เพราะมักเจอก่อกวนบ่อยจาก not autoconfirmed
    """
    if len(content) < 72 and not autoconfirmed:
        if page['ns'] % 2 == 1 or page['ns'] == 0:
            revert(page, u"ก่อกวน/ไม่เป็นสารานุกรม", newpage, makeWar = (page['ns'] == 0))
            return
    
    """
    ภาษาต่างประเทศ!
    1. วางใจ autoconfirmed
    2. ตรวจเฉพาะ ns:talk ทั้งหลาย กับ ns:main
    """
    cntThaiChar, cntForeignChar = liblang.analyzeChar(re.sub("\[\[[\w-]+:.*?\]\]\n", "", content))
    
    if not autoconfirmed and page['ns'] != 3 and (page['ns'] == 0 or page['ns'] % 2 == 1):
        if cntThaiChar * 20 <= cntForeignChar or cntThaiChar <= 10:
            revert(page, u"ภาษาต่างประเทศ", newpage)
            return
    
    lines = change.splitlines()

    cntWrongVowel = 0
    cntAddedLink = 0
    cntDeletedLink = 0
    addedLink = u""
    addedLine = u""
    deletedLine = u""
    
    for line in lines:
        line = line.strip()
        if line.startswith(u'<td class="diff-deletedline">'):
            line = re.sub(u"<td.*?>", u"", line)
            line = re.sub(u"</td>", u"", line)
            line = re.sub(u"<div>", u"", line)
            line = re.sub(u"</div>", u"", line)
            line = re.sub(u"<span.*?>", u"", line)
            line = re.sub(u"</span>", u"", line)
            line = re.sub(u"&lt;", u"<", line)
            line = re.sub(u"&gt;", u">", line)
            
            cntDeletedLink += libstring.findOverlap(u"http://", line)
            cntDeletedLink -= libstring.findOverlap(u"<ref>", line)
            deletedLine += line + u'\n'
            
        elif line.startswith(u'<td class="diff-addedline">') or newpage:
            if not newpage:
                line = re.sub(u"<td.*?>", u"", line)
                line = re.sub(u"</td>", u"", line)
                line = re.sub(u"<div>", u"", line)
                line = re.sub(u"</div>", u"", line)
                line = re.sub(u"<span.*?>", u"", line)
                line = re.sub(u"</span>", u"", line)
                line = re.sub(u"&lt;", u"<", line)
                line = re.sub(u"&gt;", u">", line)
            
            addedLine += line + u'\n'
            cntWrongVowel += liblang.cntWrongVowel(line)
            cntAddedLink += libstring.findOverlap(u"http://", line)
            cntAddedLink -= libstring.findOverlap(u"<ref>", line)
            alllink = re.findall(u"http://\w+", line)
            for i in alllink: addedLink += i
    
    """
    ก่อกวน: เพิ่มคำใน blacklist
    1. ยกเว้น autoconfirmed
    """
    if not autoconfirmed:
        for i in VandalBlacklist:
            if re.search(i, addedLine) is not None:
                revert(page, u"ก่อกวน", newpage)
                return
    
    """
    ไม่เป็นสารานุกรม
    1. ตรวจหมด รวม autoconfirmed ด้วย
    """
    for subject in NotEncyList:
        lim = len(subject[0]) if subject[2] == const['UNLIM'] else subject[2]
        cnt = 0
        for x in subject[0]:
            if re.search(x, addedLine) is not None:
                cnt += 1
        
        if cnt == lim:
            revert(page, subject[1], newpage, makeWar = True)
            return
    
    """
    สแปม
    1. ไม่ตรวจ autoconfirmed ซึ่งอาจจะแทรกลิงก์เจตนาดี
    """
    if not autoconfirmed and (len(addedLink) * 5 >= len(addedLine)) and cntAddedLink > cntDeletedLink and \
        isSpam(page['title'], revision[1]['revid'], page['revisions'][0]['user']):
        revert(page, u"สแปม", newpage)
        return
    
    """
    ก่อกวน: สระซ้อนเยอะเกิน
    """
    if cntWrongVowel >= 13:
        revert(page, u"ก่อกวน", newpage)
        return
    
    """
    ลบข้อมูลออก
    1. วางใจ autoconfirmed
    2. ไม่สนใจการกระทำในหน้าของตัวเอง
    3. เกิน 1000 อักขระ
    """
    if not autoconfirmed and (not page['title'].startswith(u"ผู้ใช้:" + page['revisions'][0]['user'])) and \
        len(deletedLine) - len(addedLine) >= 1000:
        revert(page, u"ถูกลบข้อมูลออก", False)
        return
    
    """
    ก่อกวน
    """
    if len(addedLine) > 0 and liblang.checkRepetition(addedLine.encode("utf-8")) >= 32:
        revert(page, u"ก่อกวน", False, makeWar = True)
        return
    
    return curpage

if __name__ == "__main__":
    pywikibot.handleArgs("-log")
    pywikibot.output(u"สคริปต์ย้อนก่อกวนเริ่มทำงาน ณ เวลา %s" % libdate.getTime())
    
    if len(sys.argv) > 1:
        gen = [int(sys.argv)]
    else:
        gen = libgenerator.recentchanges(number = startChecking, namespace = "|".join([str(x) for x in xrange(16)]), repeat = True)
    
    try:
        for revision in gen: clean(check(revision))
    except:
        preload.error()
    
    pywikibot.output(u"สคริปต์ย้อนก่อกวนหยุดทำงาน ณ เวลา %s" % libdate.getTime())
    pywikibot.stopme()
