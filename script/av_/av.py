# -*- coding: utf-8 -*-

import sys, os, re, time, traceback
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try: from lib import preload
except:
    print "เรียกใช้ไลบรารีไม่ได้ จบการทำงาน!"
    sys.exit()

import query, userlib
from lib import libdate
import wikipedia as pywikibot

startChecking = 200
site = preload.site

def recentchanges(number = 100, rcstart = None, rcend = None, rcshow = ['!redirect', '!bot'],
    rcdir = 'older', rctype = 'edit|new', namespace = None, repeat = False, user = None):
    params = {
        'action'    : 'query',
        'list'      : 'recentchanges',
        'rcdir'     : rcdir,
        'rctype'    : rctype,
        'rcprop'    : ['user', 'comment', 'timestamp', 'title', 'ids',
                       'loginfo', 'sizes'], #', 'flags', 'redirect', 'patrolled'],
        'rcnamespace' : namespace,
        'rclimit'   : int(number),
    }
    
    if user: params['rcuser'] = user
    if rcstart: params['rcstart'] = rcstart
    if rcend: params['rcend'] = rcend
    if rcshow: params['rcshow'] = rcshow
    if rctype: params['rctype'] = rctype

    seen = set()
    while True:
        data = query.GetData(params)
        if 'error' in data:
            raise RuntimeError('%s' % data['error'])
        try:
            rcData = data['query']['recentchanges']
        except KeyError:
            raise ServerError("The APIs don't return data, the site may be down")

        for i in rcData:
            if i['revid'] not in seen:
                seen.add(i['revid'])
                page = pywikibot.Page(site, i['title'], defaultNamespace=i['ns'])
                if 'comment' in i:
                    page._comment = i['comment']
                yield page, i
                
        if not repeat: break
        time.sleep(10.0)

def getRevision(revid, prop):
    params = {
        'action'   : 'query',
        'prop'     : 'revisions',
        'revids'   : revid,
    }
    if prop == 'diff':
        params['rvdiffto'] = 'prev'
        return query.GetData(params, site)['query']['pages'].itervalues().next()
    elif prop == 'content':
        params['rvprop'] = 'content'
        return query.GetData(params, site)['query']['pages'].itervalues().next()['revisions'][0]['*']

def allContribute(pageName):
    params = {
        'action'   : 'query',
        'prop'     : 'revisions',
        'titles'   : pageName,
        'rvprop'   : 'user|ids',
        'rvlimit'  : 5000
    }
    return query.GetData(params, site)['query']['pages'].itervalues().next()['revisions']

def IsSpam(pageName, revision, user):
    contribs = allContribute(pageName)
    cnt = 0
    startOp = False
    for i in contribs:
        if startOp and user == i['user']: cnt += 1
        if i['revid'] == revision: startOp = True
    
    pywikibot.output(u"cnt = %s" % cnt)
    return cnt < 3

revertedDict = {}

import subprocess

def notifyOSD(s):
    try: subprocess.call(["notify-send", s.encode("utf-8")])
    except: pass

def revert(page, reason, newpage, template = False):
    summary = u"ลบ" if newpage else u"ย้อน" + u"บทความ" + reason
    pywikibot.output(page['title'] + u": " + summary)
    
    if page['title'] in revertedDict:
        if revertedDict[page['title']] > 1:
            pywikibot.output(u"อย่าก่อสงคราม! เลิกการย้อน")
            return
        revertedDict[page['title']] += 1
    else:
        revertedDict[page['title']] = 0
    
    notifyOSD(page['title'] + u": " + summary)
    
    if newpage:
        pageObject = pywikibot.Page(site, page['title'])
        if int(page['ns']) % 2 == 1:
            pageObject.put(u"{{อธิบายหน้าพูดคุย}}", summary + preload.summarySuffix, botflag = False)
        else:
            try: pageObject.put(u"{{ลบ|%s}}\n%s" % (summary, tpage.get()), 
                summary + preload.summarySuffix, botflag = False)
            except:
                pywikibot.output(u"ย้อนสำเร็จ!")
                preload.error()
            
        return
        
    params = {
        'action': 'edit',
        'pageid': page['pageid'],
        'undo'  : page['revisions'][0]['revid'],
        'summary': summary + SUFFIX,
        'token'  : site.getToken(),
        'minor'  : 1,
    }
    
    response, data = query.GetData(params, site, back_response = True)
    
    try:
        if data['edit']['result'] == u"Success":
            pywikibot.output(u"ย้อนสำเร็จ!")
        else:
            raise Exception
    except:
        print response, data
        pywikibot.output(u"ย้อน %s ไม่สำเร็จ" % page['title'])
        preload.error()
        
def findoverlap(pattern, text):
    pat = u"(?=(%s))" % pattern
    it = re.finditer(pat, text)
    cnt = 0
    for i in it: cnt += 1
    return cnt    


ALL = -1

allnotencyclo = [
    ([u"==\s*วิสัยทัศน์\s*==", u"==\s*พันธกิจ\s*=="], u"ไม่เป็นสารานุกรม (หัวข้อวิสัยทัศน์, พันธกิจ)", ALL), 
]

try:
    with open("VandalBlacklist.txt") as f:
        lines = f.readlines()
        VandalBlacklist = [x.decode("utf-8").strip() for x in lines]
        
    with open("UserBlacklist.txt") as f:
        lines = f.readlines()
        UserBlacklist = [x.decode("utf-8").strip() for x in lines]
except:
    preload.error()

def check(revision):
    newpage = False
    page = getRevision(revision[1]['revid'])
    pywikibot.output(u"กำลังตรวจสอบหน้า " + page['title'] + " ณ เวลา " + page['revisions'][0]['timestamp'])
    
    # ไฟล์ของผู้ใช้
    if page['title'].endswith(u".js") or page['title'].endswith(u".css"):
        pywikibot.output("พบไฟล์ผู้ใช้! ยกเลิกการตรวจสอบ")
        return
    
    # หน้าทดลองเขียน
    if (page['title'].startswith(u"ผู้ใช้:" + page['revisions'][0]['user']) and \
        (re.search(u"(ทดลองเขียน|กระบะทราย|กระดาษทด)", page['title']) is not None)) \
        or (re.sub("\ ", "_", page['title']) in sandbox_pages):
        pywikibot.output(u"พบหน้าทดลอง! ยกเลิกการตรวจสอบ")
        return
            
    if not page['revisions'][0]['diff']['from']:
        pywikibot.output(u"หน้านี้เป็นหน้าใหม่!")
        newpage = True
        change = getRevisionContent(revision[1]['revid'])
    else:
        change = page['revisions'][0]['diff']['*']
    
    try:
        curpage = pywikibot.Page(site, page['title'])
        content = curpage.get()
    except:
        pywikibot.output(u"ผิดพลาด: ไม่สามารถเรียกข้อมูลหน้าได้ ยกเลิกการตรวจสอบ")
        pywikibot.output(traceback.format_exc().decode("utf-8"))
        return
    
    content = re.sub(u"<!--.*?-->", u"", content, re.DOTALL)
    
    if re.search(u"\{\{(ลบ|Delete|Sd|ละเมิดลิขสิทธิ์|Copyvio).*?\}\}", content, re.IGNORECASE | re.DOTALL):
        pywikibot.output(u"มีป้ายติดอยู่แล้ว! ยกเลิกการตรวจสอบ")
        return
    
    user = userlib.User(site, page['revisions'][0]['user'])
    autoconfirmed = user.isRegistered() and ('autoconfirmed' in user.groups())
    
    content = re.sub("\[\[[\w-]+:.*?\]\]\n", "", content)

    foreignChar, Thaichar = thailang.analyzeChar(content)
    
    if page['ns'] == 0:
        if thaichar * 20 <= foreignchar or thaichar <= 10:
            revert(page, u"ภาษาต่างประเทศ", newpage)
            return
    
    lines = change.splitlines()
    
    sizetag = 0
    sizecontent = 0
    sizedeleted = 0
    sizeadded = 0
    cntvowelwrong = 0
    
    if newpage and len(content) < 72:
        revert(page, u"ไม่เป็นสารานุกรม", True)
    
    pagecontent = u""
    
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
            sizedeleted += len(line)
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
            
            sizeadded += len(line)
            if (re.search("http://", line) is not None) and (re.search("<.?ref>", line) is None):
                sizetag += len(line)
            else:
                sizecontent += len(line)
            
            pagecontent += line + u'\n'
            
            for i in blacklist:
                if re.search(i, line) is not None:
                    revert(page, u"ก่อกวน", newpage)
                    return
            
            cntvowelwrong += findoverlap(ThaiVowelFront + ThaiVowelFront, line)
            cntvowelwrong += findoverlap(ThaiVowelFront + ThaiVowelBack, line)
            cntvowelwrong += findoverlap(ThaiVowelFront + ThaiVowelUm, line)
            cntvowelwrong += findoverlap(ThaiVowelFront + ThaiVowelUp, line)
            cntvowelwrong += findoverlap(ThaiVowelFront + ThaiVowelDown, line)
            cntvowelwrong += findoverlap(ThaiVowelFront + ThaiVowelTaiku, line)
            cntvowelwrong += findoverlap(ThaiVowelFront + ThaiSound, line)
            cntvowelwrong += findoverlap(ThaiVowelFront + ThaiTantakad, line)
            cntvowelwrong += findoverlap(ThaiVowelFront + ThaiPaismall, line)
            cntvowelwrong += findoverlap(ThaiVowelFront + ThaiAgain, line)
            cntvowelwrong += findoverlap(ThaiVowelFront + EngCharString, line)
                                 
            cntvowelwrong += findoverlap(ThaiVowelBack + ThaiVowelUm, line)
            cntvowelwrong += findoverlap(ThaiVowelBack + ThaiVowelUp, line)
            cntvowelwrong += findoverlap(ThaiVowelBack + ThaiVowelDown, line)
            cntvowelwrong += findoverlap(ThaiVowelBack + ThaiVowelTaiku, line)
            cntvowelwrong += findoverlap(ThaiVowelBack + ThaiSound, line)
            cntvowelwrong += findoverlap(ThaiVowelBack + ThaiTantakad, line)
                                 
            cntvowelwrong += findoverlap(ThaiVowelUm + ThaiVowelBack, line)
            cntvowelwrong += findoverlap(ThaiVowelUm + ThaiVowelUm, line)
            cntvowelwrong += findoverlap(ThaiVowelUm + ThaiVowelUp, line)
            cntvowelwrong += findoverlap(ThaiVowelUm + ThaiVowelDown, line)
            cntvowelwrong += findoverlap(ThaiVowelUm + ThaiVowelTaiku, line)
            cntvowelwrong += findoverlap(ThaiVowelUm + ThaiSound, line)
            cntvowelwrong += findoverlap(ThaiVowelUm + ThaiTantakad, line)
                                 
            cntvowelwrong += findoverlap(ThaiVowelUp + ThaiVowelBack, line)
            cntvowelwrong += findoverlap(ThaiVowelUp + ThaiVowelUm, line)
            cntvowelwrong += findoverlap(ThaiVowelUp + ThaiVowelUp, line)
            cntvowelwrong += findoverlap(ThaiVowelUp + ThaiVowelDown, line)
            cntvowelwrong += findoverlap(ThaiVowelUp + ThaiVowelTaiku, line)
                                 
            cntvowelwrong += findoverlap(ThaiVowelDown + ThaiVowelBack, line)
            cntvowelwrong += findoverlap(ThaiVowelDown + ThaiVowelUm, line)
            cntvowelwrong += findoverlap(ThaiVowelDown + ThaiVowelUp, line)
            cntvowelwrong += findoverlap(ThaiVowelDown + ThaiVowelDown, line)
            cntvowelwrong += findoverlap(ThaiVowelDown + ThaiVowelTaiku, line)
                                 
            cntvowelwrong += findoverlap(ThaiVowelTaiku + ThaiVowelBack, line)
            cntvowelwrong += findoverlap(ThaiVowelTaiku + ThaiVowelUm, line)
            cntvowelwrong += findoverlap(ThaiVowelTaiku + ThaiVowelUp, line)
            cntvowelwrong += findoverlap(ThaiVowelTaiku + ThaiVowelDown, line)
            cntvowelwrong += findoverlap(ThaiVowelTaiku + ThaiVowelTaiku, line)
            cntvowelwrong += findoverlap(ThaiVowelTaiku + ThaiTantakad, line)
                                 
            cntvowelwrong += findoverlap(ThaiSound + ThaiVowelUp, line)
            cntvowelwrong += findoverlap(ThaiSound + ThaiVowelDown, line)
            cntvowelwrong += findoverlap(ThaiSound + ThaiVowelTaiku, line)
            cntvowelwrong += findoverlap(ThaiSound + ThaiSound, line)
            cntvowelwrong += findoverlap(ThaiSound + ThaiTantakad, line)
                                 
            cntvowelwrong += findoverlap(ThaiTantakad + ThaiVowelBack, line)
            cntvowelwrong += findoverlap(ThaiTantakad + ThaiVowelUm, line)
            cntvowelwrong += findoverlap(ThaiTantakad + ThaiVowelUp, line)
            cntvowelwrong += findoverlap(ThaiTantakad + ThaiVowelDown, line)
            cntvowelwrong += findoverlap(ThaiTantakad + ThaiVowelTaiku, line)
            cntvowelwrong += findoverlap(ThaiTantakad + ThaiSound, line)
            cntvowelwrong += findoverlap(ThaiTantakad + ThaiTantakad, line)
                                 
            cntvowelwrong += findoverlap(ThaiPaismall + ThaiVowelBack, line)
            cntvowelwrong += findoverlap(ThaiPaismall + ThaiVowelUm, line)
            cntvowelwrong += findoverlap(ThaiPaismall + ThaiVowelUp, line)
            cntvowelwrong += findoverlap(ThaiPaismall + ThaiVowelDown, line)
            cntvowelwrong += findoverlap(ThaiPaismall + ThaiVowelTaiku, line)
            cntvowelwrong += findoverlap(ThaiPaismall + ThaiSound, line)
            cntvowelwrong += findoverlap(ThaiPaismall + ThaiTantakad, line)
            cntvowelwrong += findoverlap(ThaiPaismall + ThaiPaismall, line)
            cntvowelwrong += findoverlap(ThaiPaismall + ThaiAgain, line)
                                 
            cntvowelwrong += findoverlap(ThaiAgain + ThaiVowelFront, line)
            cntvowelwrong += findoverlap(ThaiAgain + ThaiVowelBack, line)
            cntvowelwrong += findoverlap(ThaiAgain + ThaiVowelUm, line)
            cntvowelwrong += findoverlap(ThaiAgain + ThaiVowelUp, line)
            cntvowelwrong += findoverlap(ThaiAgain + ThaiVowelDown, line)
            cntvowelwrong += findoverlap(ThaiAgain + ThaiVowelTaiku, line)
            cntvowelwrong += findoverlap(ThaiAgain + ThaiSound, line)
            cntvowelwrong += findoverlap(ThaiAgain + ThaiTantakad, line)
            cntvowelwrong += findoverlap(ThaiAgain + ThaiPaismall, line)                
                                 
            cntvowelwrong += findoverlap(EngCharString + ThaiVowelBack, line)
            cntvowelwrong += findoverlap(EngCharString + ThaiVowelUm, line)
            cntvowelwrong += findoverlap(EngCharString + ThaiVowelUp, line)
            cntvowelwrong += findoverlap(EngCharString + ThaiVowelDown, line)
            cntvowelwrong += findoverlap(EngCharString + ThaiVowelTaiku, line)
            cntvowelwrong += findoverlap(EngCharString + ThaiSound, line)
            cntvowelwrong += findoverlap(EngCharString + ThaiTantakad, line)
            cntvowelwrong += findoverlap(u"\w" + ThaiPaismall, line)
            cntvowelwrong += findoverlap(u"\w" + ThaiAgain, line)
            
    for subject in allnotencyclo:
        lim = len(subject[0]) if subject[2] == ALL else subject[2]
        cnt = 0
        for x in subject[0]:
            if re.search(x, pagecontent) is not None:
                cnt += 1
        
        if cnt == lim: revert(page, subject[1], newpage)
    
    if sizetag == 0: pywikibot.output(u"This user does not spam :)")
    elif (sizetag * 5 >= sizecontent) and \
        checkpagespam(page['title'], revision[1]['revid'], page['revisions'][0]['user']):
        revert(page, u"สแปม", newpage)
        return
    else:
        pywikibot.output(u"Link found but it seems that he doesn't spam")
    
    pywikibot.output(u"incorrect vowel = %d" % cntvowelwrong)
    if cntvowelwrong >= 13:
        revert(page, u"ก่อกวน", newpage)
        return
    else:
        pywikibot.output(u"This is not vandalized edition")
    
    if (not page['title'].startswith(u"ผู้ใช้:" + page['revisions'][0]['user'])) and \
        sizedeleted - sizeadded >= 1000:
        revert(page, u"ถูกลบข้อมูลออก", False)
        return
        
if __name__ == "__main__":
    pywikibot.handleArgs("-log")
    pywikibot.output(u"สคริปต์ย้อนก่อกวนเริ่มทำงาน ณ เวลา %s" % libdate.getTime())
    
    gen = recentchanges(number = MINCHECK, namespace = "|".join([str(x) for x in xrange(16)]), repeat = True)
    
    try:
        for revision in gen: check(revision)
    except:
        pywikibot.output(u"สคริปต์ย้อนก่อกวนหยุดทำงาน ณ เวลา %s" % libdate.getTime())
        preload.error()
        pywikibot.stopme()
