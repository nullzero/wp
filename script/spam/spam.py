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

def recentchanges(number = 100, rcstart = None, rcend = None, rcshow = ['!redirect'],
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

reverteddict = {}

def revert(page, summary):
    pywikibot.output(page['title'] + u": " + summary)
    
    if page['title'] in reverteddict:
        if reverteddict[page['title']] >= 3:
            pywikibot.output(u"Don't make a war!")
            return
        reverteddict[page['title']] += 1
    else:
        reverteddict[page['title']] = 0
        
    params = {
        'action': 'edit',
        'pageid': page['pageid'],
        'undo'  : page['revisions'][0]['revid'],
        'summary': summary,
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
    
    gen = recentchanges(number = 20, namespace = "|".join([str(x) for x in xrange(16)]), repeat = True)
    for revision in gen:
        newpage = False
        page = getRevision(revision[1]['revid'])
        pywikibot.output(u"I'm checking " + page['title'])
        
        user = userlib.User(site, page['revisions'][0]['user'])
        if user.isRegistered():
            if 'autoconfirmed' in user.groups():
                pywikibot.output(u"I trust you!")
                continue
                
        if page['revisions'][0]['diff']['from'] == u"":
            pywikibot.output(u"This is a new page")
            newpage = True
            change = page.get()
        else:
            change = page['revisions'][0]['diff']['*']
            
        lines = change.splitlines()
        
        sizetag = 0
        sizecontent = 0
        linetag = 0
        linecontent = 0
        
        for line in lines:
            line = line.strip()
            if line.startswith(u'<td class="diff-addedline">'):
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
                revert(page, u"ย้อนบทความภาษาต่างประเทศ หากผิดพลาดโปรดแจ้ง[[คุยกับผู้ใช้:Nullzero|ที่นี่]]")
            else:
                pywikibot.output(u"ภาษาไทยครับ!")
        
        if sizetag == 0:
            pywikibot.output(u"This user does not spam :)")
            continue
        
        if (sizetag * 30 >= sizecontent) or (linetag * 30 >= linecontent):
            revert(page, u"ย้อนการสแปมอัตโนมัติ หากผิดพลาดโปรดแจ้ง[[คุยกับผู้ใช้:Nullzero|ที่นี่]]")
        else:
            pywikibot.output(u"Link found but not frequent enough")
        
    pywikibot.output(u"'spam script' terminated. (%s)" % libdate.getTime())
    pywikibot.stopme()
