# -*- coding: utf-8 -*-

import sys, os, re, time, traceback
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try: from lib import preload
except:
    print "Cannot import preload. Exit!"
    sys.exit()

import query, userlib
from lib import libdate
import wikipedia as pywikibot

site = pywikibot.getSite()

def recentchanges(number = 100, rcstart = None, rcend = None, rcshow = ['!redirect', '!bot'],
    rcdir = 'older', rctype = 'edit|new', namespace = None, repeat = False, user = None):
    """
    Yield recent changes as Page objects
    uses API call: action=query&list=recentchanges&rctype=edit|new&rclimit=500

    Starts with the newest change and fetches the number of changes
    specified in the first argument. If repeat is True, it fetches
    again.

    Options directly from APIs:
    ---
    Parameters:
      rcstart        - The timestamp to start enumerating from.
      rcend          - The timestamp to end enumerating.
      rcdir          - In which direction to enumerate.
                       One value: newer, older
                       Default: older
      rcnamespace    - Filter log entries to only this namespace(s)
                       Values (separate with '|'):
                       0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15
      rcprop         - Include additional pieces of information
                       Values (separate with '|'):
                       user, comment, flags, timestamp, title, ids, sizes,
                       redirect, patrolled, loginfo
                       Default: title|timestamp|ids
      rcshow         - Show only items that meet this criteria.
                       For example, to see only minor edits done by
                       logged-in users, set show=minor|!anon
                       Values (separate with '|'):
                       minor, !minor, bot, !bot, anon, !anon,
                       redirect, !redirect, patrolled, !patrolled
      rclimit        - How many total changes to return.
                       No more than 500 (5000 for bots) allowed.
                       Default: 10
      rctype         - Which types of changes to show.
                       Values (separate with '|'): edit, new, log

    The objects yielded are dependent on parmater returndict.
    When true, it yields a tuple composed of a Page object and a dict of attributes.
    When false, it yields a tuple composed of the Page object,
    timestamp (unicode), length (int), an empty unicode string, username
    or IP address (str), comment (unicode).

    # TODO: Detection of unregistered users is broken
    """
    
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

def getRevision(revid):
    params = {
        'action'   : 'query',
        'prop'     : 'revisions',
        'revids'   : revid,
        'rvdiffto' : 'prev',
    }
    return query.GetData(params, site)['query']['pages'].itervalues().next()

def getRevisionContent(revid):
    params = {
        'action'   : 'query',
        'prop'     : 'revisions',
        'revids'   : revid,
        'rvprop'   : 'content',
    }
    return query.GetData(params, site)['query']['pages'].itervalues().next()['revisions'][0]['*']

def allContribute(pagename):
    params = {
        'action'   : 'query',
        'prop'     : 'revisions',
        'titles'   : pagename,
        'rvprop'   : 'user|ids',
        'rvlimit'  : 5000
    }
    return query.GetData(params, site)['query']['pages'].itervalues().next()['revisions']

def checkpagespam(pagename, revision, user):
    contribs = allContribute(pagename)
    cnt = 0
    startOp = False
    for i in contribs:
        if startOp and user == i['user']: cnt += 1
        if i['revid'] == revision: startOp = True
    
    pywikibot.output(u"cnt = %s" % cnt)
    return cnt < 3

reverteddict = {}

SUFFIX = u" หากผิดพลาดโปรดแจ้ง[[คุยกับผู้ใช้:Nullzero|ที่นี่]]"

import subprocess

def notifyosd(s):
    try: subprocess.call(["notify-send", s.encode("utf-8")])
    except: pass

def revert(page, reason, newpage):
    action = u"ลบ" if newpage else u"ย้อน"
    summary = action + u"บทความ" + reason
    pywikibot.output(page['title'] + u": " + summary)
    notifyosd(page['title'] + u": " + summary)
    
    if page['title'] in reverteddict:
        if reverteddict[page['title']] > 1:
            pywikibot.output(u"Don't make a war!")
            return
        reverteddict[page['title']] += 1
    else:
        reverteddict[page['title']] = 0
    
    if newpage:
        tpage = pywikibot.Page(site, page['title'])
        if int(page['ns']) % 2 == 1:
            tpage.put(u"{{อธิบายหน้าพูดคุย}}", summary + SUFFIX)
        else:
            if (int(page['ns']) != 0) and (re.search(u"(ทดลองเขียน|กระบะทราย|กระดาษทด)", page['title']) is not None):
                pywikibot.output(u"หน้าทดลอง")
            else:
                try: tpage.put(u"{{ลบ|" + summary + "}}\n" + tpage.get(), summary + SUFFIX)
                except: pywikibot.output(traceback.format_exc().decode("utf-8"))
        return
        
    params = {
        'action': 'edit',
        'pageid': page['pageid'],
        'undo'  : page['revisions'][0]['revid'],
        'summary': summary + SUFFIX,
        'token'  : site.getToken(),
        'bot'    : 1,
        'minor'  : 1,
    }
    
    response, data = query.GetData(params, site, back_response = True)
    
    try:
        if data['edit']['result'] == u"Success":
            pywikibot.output(u"Succeeded!")
        else:
            raise Exception
    except:
        print response, data
        pywikibot.output(u"Unsucceed to revert" + page['title'])
        
def findoverlap(pattern, text):
    pat = u"(?=(%s))" % pattern
    it = re.finditer(pat, text)
    cnt = 0
    for i in it: cnt += 1
    return cnt

ThaiChar = [unichr(x) for x in xrange(ord(u'ก'), ord(u'ฮ') + 1)]
EngCharString = u""
ThaiCharString = u""
for i in xrange(128): EngCharString += unichr(i)
for i in ThaiChar: ThaiCharString += i
EngCharString = u"[" + EngCharString + u"]"
ThaiCharString = u"[" + ThaiCharString + u"]"
ThaiVowelFront = u"[เแโใไ]"
ThaiVowelBack = u"[ะาๅ]"
ThaiVowelUm = u"[ำ]"
ThaiVowelUp = u"[ัิีึืํ]"
ThaiVowelDown = u"[ฺุู]"
ThaiVowelTaiku = u"[็]"
ThaiSound = u"[่้๊๋]"
ThaiTantakad = u"[์]"
ThaiPaismall = u"[ฯ]"
ThaiAgain = u"[ๆ]"
#autobio = [u"ชื่อเล่น", u"ส่วนสูง", u"น้ำหนัก", u"เกิด.*วัน", u"(จบ|เรียน|ศึกษา)", u"(facebook|เฟ[สซ]บุ๊[กค]|twitter)", u"อีเมล", u"เว็?[บป]"]
vlist = []
vlist.append(u"วิกิพีเดีย:สอนการใช้งาน_(จัดรูปแบบ)/กระดาษทด")
vlist.append(u"วิกิพีเดีย:สอนการใช้งาน_(แหล่งข้อมูลอื่น)/กระดาษทด")
vlist.append(u"วิกิพีเดีย:สอนการใช้งาน_(แก้ไข)/กระดาษทด")
vlist.append(u"วิกิพีเดีย:สอนการใช้งาน_(วิกิพีเดียลิงก์)/กระดาษทด")
vlist.append(u"วิกิพีเดีย:ทดลองเขียน")

with open("blacklist.txt") as f:
    lines = f.readlines()
    blacklist = [x.decode("utf-8").strip() for x in lines]

with open("userblacklist.txt") as f:
    lines = f.readlines()
    userblacklist = [x.decode("utf-8").strip() for x in lines]

def check(revision):
    newpage = False
    page = getRevision(revision[1]['revid'])
    pywikibot.output(u"I'm checking " + page['title'] + " @ " + page['revisions'][0]['timestamp'])
    
    if page['title'].endswith(u".js") or page['title'].endswith(u".css"):
        pywikibot.output("It's a file!")
        return
            
    user = userlib.User(site, page['revisions'][0]['user'])
    if user.isRegistered():
        if 'autoconfirmed' in user.groups():
            pywikibot.output(u"I trust you!")
            return
            
    if not page['revisions'][0]['diff']['from']:
        pywikibot.output(u"This is a new page")
        newpage = True
        change = getRevisionContent(revision[1]['revid'])
    else:
        change = page['revisions'][0]['diff']['*']
    
    try:
        curpage = pywikibot.Page(site, page['title'])
        content = curpage.get()
    except:
        pywikibot.output(u"Can't get page content!")
        pywikibot.output(traceback.format_exc().decode("utf-8"))
        return
    
    if re.search(u"\{\{(ลบ|Delete|Sd|ละเมิดลิขสิทธิ์|Copyvio).*?\}\}", 
        content, re.IGNORECASE | re.DOTALL):
        pywikibot.output(u"There exist a label!")
        return
    
    if re.sub("\ ", "_", page['title']) not in vlist:
        foreignchar = 0
        thaichar = 0
        
        content = re.sub("\[\[[\w-]+:.*?\]\]\n", "", content)
    
        for i in content:
            if i in ThaiChar: thaichar += 1
            elif ord(i) > ord(u' '): foreignchar += 1
        
        if page['ns'] == 0:
            if thaichar * 20 <= foreignchar or thaichar <= 10:
                revert(page, u"ภาษาต่างประเทศ", newpage)
                return
            else:
                pywikibot.output(u"ภาษาไทยครับ!")
    
    """
    for user in userblacklist:
        if re.search(user, page['revisions'][0]['user']) is not None:
            revert(page, u"ก่อกวน", newpage)
            return
    """
    
    lines = change.splitlines()
    
    sizetag = 0
    sizecontent = 0
    sizedeleted = 0
    sizeadded = 0
    cntvowelwrong = 0
    #cntautobio = 0
    
    """
    for i in autobio:
        if re.search(i, line) is not None:
            print i
            cntautobio += 1
    """
    
    #if len(content) < 500: cntautobio += 1
    
    if newpage and len(content) < 72:
        revert(page, u"ไม่เป็นสารานุกรม", True)
    
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
    
    """
    if cntautobio >= 5:
        revert(page, u"อัตชีวะประวัติ", newpage)
    """
        
if __name__ == "__main__":
    pywikibot.handleArgs("-log")
    pywikibot.output(u"'spam script' is invoked. (%s)" % libdate.getTime())
    
    gen = recentchanges(number = 20, namespace = "|".join([str(x) for x in xrange(16)]), repeat = True)
    for revision in gen: check(revision)
        
    pywikibot.output(u"'spam script' terminated. (%s)" % libdate.getTime())
    pywikibot.stopme()
