# -*- coding: utf-8 -*-

DEBUG = False

import sys, os, re, time, traceback, urllib, subprocess
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try: from lib import preload
except:
    print "เรียกใช้ไลบรารีไม่ได้ จบการทำงาน!"
    sys.exit()

import query, userlib
from lib import libdate, liblang, libstring, libgenerator, librevision, miscellaneous
import wikipedia as pywikibot

startChecking = 5
site = preload.site
env = preload.env

const = {
    'UNLIM' : -1,
}

NotEncyList = [
    ([u"==\s*วิสัยทัศน์\s*==", u"==\s*พันธกิจ\s*=="], u"วิสัยทัศน์ฯ ไม่เป็นสาราฯ", const['UNLIM']), 
    ([u"สัญญลักษณ์"], u"แปลจาก google translate", 1),
    ([u"!!\s*((แสดง)?คู่(กับ)?|นักแสดงร่วม)", u"!!\s*ออกอากาศ"], u"ตาม[[วิกิพีเดีย:โครงการวิกิภาพยนตร์/รูปแบบการเขียน/บทความนักแสดง]]", 1),
    ([u"Example.jpg"], u"ไม่เป็นสาราฯ", 1)
]

def readFileList(vector, filename):
    with open(preload.File(__file__, filename), "r") as f:
        dat = [x.strip().decode("utf-8").replace(u"\u200e", u"") for x in f.read().split() if x.strip() != ""]
        for i in dat: vector.append(i)

try:
    VandalBlacklist = []
    UserBlacklist = []
    UserWhitelist = []
    
    readFileList(VandalBlacklist, "VandalBlacklist.txt")
    readFileList(UserBlacklist, "UserBlacklist.txt")
    readFileList(UserWhitelist, "UserWhitelist.txt")
except:
    preload.error()

def isSpam(pageName, revision, user):
    contribs = librevision.allContribute(pageName)
    cnt = 0
    startOp = False
    for i in contribs:
        if startOp and user == i['user']: cnt += 1
        if i['revid'] == revision: startOp = True
    
    pywikibot.output(u"เค้าคนนี้แก้หน้านี้มาแล้ว %s ครั้ง" % cnt)
    return cnt == 0

def notifyOSD(s):
    try: subprocess.call(["notify-send", s.encode("utf-8")])
    except: pass

def delete(page, reason, labelDelete = False):
    pywikibot.output(u">>> ลบ: " + page['title'] + u": " + reason)
    notifyOSD(u"ลบ: " + page['title'] + u": " + reason)
    summary = reason
    pageObject = pywikibot.Page(site, page['title'])
    try:
        if int(page['ns']) % 2 == 1 and not labelDelete:
            pageObject.put(u"{{อธิบายหน้าพูดคุย}}", summary + preload.summarySuffix, botflag = False, force = True)
        else:
            pageObject.put(u"{{ลบ|" + summary + "}}\n" + pageObject.get(), summary + preload.summarySuffix, botflag = False, force = True)
    except: preload.error()

revertedDict = {}

def revert(page, reason, newpage, template = None, makeWar = False):
    pywikibot.output(u">>> ย้อน/ลบ: " + page['title'] + u": " + reason)
    notifyOSD(u"ย้อน/ลบ: " + page['title'] + u": " + reason)
    
    if not makeWar:
        if page['title'] in revertedDict:
            if revertedDict[page['title']] > 0:
                pywikibot.output(u"อย่ามีสงครามกันเลย!")
                return
            revertedDict[page['title']] += 1
        else:
            revertedDict[page['title']] = 0
    
    summary = (u"ลบ" if newpage else u"ย้อน") + u"บทความ" + reason
    
    if newpage:
        delete(page, summary)
        return
    
    librevision.revert(page['pageid'], 
        page['revisions'][0]['revid'], 
        summary, 
        page['title'])

reserveChar = [x for x in u"/-._"]
reserveCharEn = [u"%2F", u"%2D", u"%2E", u"%5F"]
patHTML = u"(https?://.*?)(?=(<\s*/\s*ref\s*>|\s|\]|$))"

def decoder(url):
    url = url.group(1)
    url = re.sub(u"%[0-7]\w", lambda x: u"~place~holder~(%s)" % x.group(), url)
    url = urllib.unquote(url.encode("utf-8")).decode("utf-8")
    for ch in xrange(len(reserveChar)):
        url = url.replace(u"~place~holder~(" + reserveChar[ch] + u")", reserveCharEn[ch])
    url = re.sub(u"~place~holder~\((.+?)\)", lambda x: urllib.quote(x.group(1)), url)
    print url
    return url

def clean(page):
    if page is None: return
    pywikibot.output(u"ผ่านครับ! เริ่มเก็บกวาดกัน")
    ocontent = page.get()
    content = ocontent
    """
    แก้สระซ้อน
    """
    content = liblang.fixRepetedVowel(content)
    """
    ลบ trailing space
    """
    content = re.sub(u"(?<!=)[ \t\r\f\v]+$", u"", content, flags = re.MULTILINE)
    """
    decode HTML เพื่อความสะอาด
    """
    '''
    try: content = re.sub(patHTML, decoder, content, re.DOTALL)
    except: preload.error()
    '''
    if content != ocontent:
        try: page.put(content, u"โรบอต: เก็บกวาด", force = True)
        except: preload.error()
            
    liblang.fixRepetedVowelTitle(page)

def imageCheckFail(content, user):
    pass

def check(revision):
    """
    มาดูกันก่อนเลย ก่อกวนหรือไม่!
    """
    newpage = False
    page = librevision.getRevision(revision[1]['revid'], 'diff')
    if DEBUG and page['title'] != env['SANDBOX'].decode("utf-8"): return
    
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
        
    """
    ยกเว้นทุกอย่างให้ sysop และ whitelist ... และตัวบอตเอง
    """
    user = userlib.User(site, page['revisions'][0]['user'])
    
    if (page['title'] != env['SANDBOX'].decode("utf-8")) and \
        user.isRegistered() and (('sysop' in user.groups()) or \
        (page['revisions'][0]['user'] in UserWhitelist) or \
        (page['revisions'][0]['user'] == env['USER'].decode("utf-8"))):
        pywikibot.output(u"คนดีเขียนครับ!")
        return curpage
        
    autoconfirmed = user.isRegistered() and ('autoconfirmed' in user.groups()) and \
        (page['title'] != env['SANDBOX'].decode("utf-8"))
    
    """
    ผู้ใช้ก่อกวน - ความสามารถนี้ใช้เฉพาะกิจและใช้เมื่อไม่มีความสามารถผู้ดูแลระบบ โปรดหลีกเลี่ยงการใช้หากเป็นไปได้
    """
    
    if page['revisions'][0]['user'] in UserBlacklist:
        revert(page, u"ก่อกวน", newpage, makeWar = (page['ns'] == 0))
    '''
    """
    ยกเลิกการตรวจสอบ: มีป้ายแล้ว
    """
    if re.search(u"\{\{(ลบ|Delete|Sd|ละเมิดลิขสิทธิ์|Copyvio).*?\}\}", content, re.IGNORECASE | re.DOTALL):
        pywikibot.output(u"!!! มีป้ายติดอยู่แล้ว! ยกเลิกการตรวจสอบ")
        return
    
    """
    ยกเลิกการตรวจสอบ: ไฟล์ของผู้ใช้
    TODO: หวังว่าคงไม่เจอสแปมในหน้านี้นะ
    """
    if page['title'].endswith(u".js") or page['title'].endswith(u".css"):
        pywikibot.output("!!! พบไฟล์ผู้ใช้! ยกเลิกการตรวจสอบ")
        return
    
    """
    ยกเลิกการตรวจสอบ: หน้าทดลองเขียน
    TODO: หวังว่าคงไม่เจอสแปมในหน้านี้นะ
    """
    if (not page['title'].startswith(env['SANDBOX'].decode("utf-8"))) and \
        (page['title'].startswith(u"ผู้ใช้:" + page['revisions'][0]['user']) and \
        (re.search(u"(ทดลองเขียน|กระบะทราย|กระดาษทด)", page['title']) is not None)) \
        or (re.sub("\ ", "_", page['title']) in miscellaneous.sandboxPages):
        pywikibot.output(u"!!! พบหน้าทดลอง! ยกเลิกการตรวจสอบ")
        return curpage
    
    if not page['revisions'][0]['diff']['from']:
        pywikibot.output(u"หน้านี้เป็นหน้าใหม่!")
        newpage = True
        change = librevision.getRevision(revision[1]['revid'], 'content')
    else:
        change = page['revisions'][0]['diff']['*']
    
    """
    ก่อกวนหรือไม่เป็นสารานุกรม เพราะ ความยาวสั้นจัด
    1. ยกเว้น autoconfirmed
    2. ไม่ใช่ ns:main เพราะอาจจะเจอพวก {{ดูเพิ่ม}} ใน ns:cat หรือ ns:template ที่สั้นจัด
    3. ตรวจหน้าพูดคุย เพราะมักเจอก่อกวนบ่อยจาก not autoconfirmed
    """
    if len(content) < 72 and not autoconfirmed:
        revert(page, u"ก่อกวน/ไม่เป็นสารานุกรม", newpage, makeWar = (page['ns'] == 0))
        return
    
    """
    หน้าที่ขึ้นกับหน้าว่าง
    """
    if page['ns'] % 2 == 1 and page['ns'] != 3:
        if not miscellaneous.existPage(pywikibot.Page(site,
            re.sub(u".*?:", u"", page['title']), defaultNamespace=int(page['ns'] - 1)).title()):
            delete(page, u"หน้าที่ขึ้นกับหน้าว่าง", labelDelete = True)
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
            deletedLine += line + u"\n"
            
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
            
            addedLine += line.rstrip() + u"\n"
            cntWrongVowel += liblang.cntWrongVowel(line)
            cntAddedLink += libstring.findOverlap(u"http://", line)
            cntAddedLink -= libstring.findOverlap(u"<ref>", line)
            alllink = re.findall(patHTML, line)
            for i in alllink: addedLink += i[0]
    
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
    if not autoconfirmed and (len(addedLink) * 5 >= len(addedLine)) and \
        cntAddedLink > cntDeletedLink and \
        isSpam(page['title'], revision[1]['revid'], page['revisions'][0]['user']):
        revert(page, u"สแปม", newpage)
        return
    
    """
    ก่อกวน: สระซ้อนเยอะเกิน
    """
    pywikibot.output(u"มีสระซ้อน %d" % cntWrongVowel)
    if cntWrongVowel >= 13:
        revert(page, u"ก่อกวน", newpage)
        return
    
    """
    ลบข้อมูลออก
    1. วางใจ autoconfirmed
    2. ไม่สนใจการกระทำในหน้าของตัวเอง
    3. เกิน 1000 อักขระ
    4. เพิ่มข้อมูลต่ำกว่า 32 เท่าของข้อมูลที่ลบ
    """
    if not autoconfirmed and (not page['title'].startswith(u"ผู้ใช้:" + page['revisions'][0]['user'])) and \
        len(deletedLine) >= 10 * len(addedLine) and len(deletedLine) >= 1000:
        revert(page, u"ถูกลบข้อมูลออก", False)
        return
        
    """
    ก่อกวนโดยการใส่ข้อมูลซ้ำ ๆ กัน
    """
    #if page['title'] not in NoRepetitionChecking:
    repetition = liblang.checkRepetition(addedLine)
    pywikibot.output(u"ข้อมูลซ้ำ %d ไบต์" % repetition)
    if len(addedLine) > 0 and repetition >= 100:
        revert(page, u"ก่อกวน", False, makeWar = True)
        return
    
    if page['title'].startswith(u"ไฟล์:"):
        if imageCheckFail(content, page['revisions'][0]['user']): return
    '''
    return curpage

if __name__ == "__main__":
    pywikibot.handleArgs("-log")
    pywikibot.output(u"สคริปต์ย้อนก่อกวนเริ่มทำงาน ณ เวลา %s" % libdate.getTime())
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "-d": DEBUG = True
        
    gen = libgenerator.recentchanges(number = startChecking, namespace = "|".join([str(x) for x in xrange(16)]), repeat = True)
    
    try:
        for revision in gen: clean(check(revision))
    except:
        preload.error()
    
    pywikibot.output(u"สคริปต์ย้อนก่อกวนหยุดทำงาน ณ เวลา %s" % libdate.getTime())
    pywikibot.stopme()

#   clean(pywikibot.Page(site, u"คุยกับผู้ใช้:Jutiphan"))
