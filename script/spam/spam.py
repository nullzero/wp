# -*- coding: utf-8 -*-

import sys, os, re, time
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

def revert(page, reason, newpage):
    action = u"ลบ" if newpage else u"ย้อน"
    summary = action + u"บทความ" + reason
    pywikibot.output(page['title'] + u": " + summary)
    
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
                tpage.put(u"{{ลบ|" + summary + "}}", summary + SUFFIX)
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
        
if __name__ == "__main__":
    pywikibot.handleArgs("-log")
    pywikibot.output(u"'spam script' is invoked. (%s)" % libdate.getTime())
    
    ThaiChar = [unichr(x) for x in xrange(ord(u'ก'), ord(u'ฮ') + 1)]
    vlist = []
    vlist.append(u"วิกิพีเดีย:สอนการใช้งาน_(จัดรูปแบบ)/กระดาษทด")
    vlist.append(u"วิกิพีเดีย:สอนการใช้งาน_(แหล่งข้อมูลอื่น)/กระดาษทด")
    vlist.append(u"วิกิพีเดีย:สอนการใช้งาน_(แก้ไข)/กระดาษทด")
    vlist.append(u"วิกิพีเดีย:สอนการใช้งาน_(วิกิพีเดียลิงก์)/กระดาษทด")
    vlist.append(u"วิกิพีเดีย:ทดลองเขียน")
    
    gen = recentchanges(number = 5, namespace = "|".join([str(x) for x in xrange(16)]), repeat = True)
    for revision in gen:
        newpage = False
        page = getRevision(revision[1]['revid'])
        pywikibot.output(u"I'm checking " + page['title'] + " @ " + page['revisions'][0]['timestamp'])
        
        user = userlib.User(site, page['revisions'][0]['user'])
        if user.isRegistered():
            if 'autoconfirmed' in user.groups():
                pywikibot.output(u"I trust you!")
                continue
                
        if not page['revisions'][0]['diff']['from']:
            pywikibot.output(u"This is a new page")
            newpage = True
            change = getRevisionContent(revision[1]['revid'])
        else:
            change = page['revisions'][0]['diff']['*']
        
        if re.search("\{\{(ลบ|Delete|Sd|ละเมิดลิขสิทธิ์|Copyvio|ละเมิดลิขสิทธิ์วัน).*?\}\}", 
            change, re.IGNORECASE | re.DOTALL):
            pywikibot.output(u"There exist a label!")
            continue
        
        if re.sub("\ ", "_", page['title']) not in vlist:
            foreignchar = 0
            thaichar = 0
        
            curpage = pywikibot.Page(site, page['title'])
            content = curpage.get()
            content = re.sub("\[\[[\w-]+:.*?\]\]\n", "", content)
        
            for i in content:
                if i in ThaiChar: thaichar += 1
                elif ord(i) > ord(u' '): foreignchar += 1
            
            if (thaichar <= 10) or (thaichar * 30 <= foreignchar):
                revert(page, u"ภาษาต่างประเทศ", newpage)
            else:
                pywikibot.output(u"ภาษาไทยครับ!")
        
        lines = change.splitlines()
        
        sizetag = 0
        sizecontent = 0
        linetag = 0
        linecontent = 0
        
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
                    
                if (re.search("http://", line) is not None) and (re.search("<.?ref>", line) is None):
                    sizetag += len(line)
                    linetag += 1
                else:
                    sizecontent += len(line)
                    linecontent += 1
        
        if sizetag == 0:
            pywikibot.output(u"This user does not spam :)")
            continue
        
        if (sizetag * 10 >= sizecontent) and \
            checkpagespam(page['title'], revision[1]['revid'], page['revisions'][0]['user']):
            revert(page, u"สแปม", newpage)
        else:
            pywikibot.output(u"Link found but it seems that he doesn't spam")
        
    pywikibot.output(u"'spam script' terminated. (%s)" % libdate.getTime())
    pywikibot.stopme()
