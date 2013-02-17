# -*- coding: utf-8 -*-

import sys, os, time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try: from lib import preload
except:
    print "เรียกใช้ไลบรารีไม่ได้ จบการทำงาน!"
    sys.exit()

from wikipedia import *

"""
linkedPages ============================================================
"""

def extractLinkedPages(content, page, withImageLinks=False):
    result = []
    try:
        thistxt = removeLanguageLinks(content,
                                      page.site())
    except NoPage:
        raise
    except IsRedirectPage:
        raise
    except SectionError:
        return []
    thistxt = removeCategoryLinks(thistxt, page.site())

    # remove HTML comments, pre, nowiki, and includeonly sections
    # from text before processing
    thistxt = removeDisabledParts(thistxt)

    # resolve {{ns:-1}} or {{ns:Help}}
    thistxt = page.site().resolvemagicwords(thistxt)

    for match in Rlink.finditer(thistxt):
        title = match.group('title')
        title = title.replace("_", " ").strip(" ")
        title = re.sub('#.*', '', title) # don't process section
        if not title: continue # skip internal section link case
        if title.startswith('//'): continue # [[//abc]] will produce an external link to http://abc
        if title.endswith('/..'): continue # such as [[a/b/..]], [[../..]]. they will not produce a link    
        if title == '..': continue # [[..]] will not produce a link
        if title.startswith('/') and '/../' in title: continue  # [[/foo/../bar]] will not produce a link
        if page.namespace() in page.site.family.namespacesWithSubpage:
            # convert relative link to absolute link if that namespace has subpage
            if title.startswith('/'):
                title = page.title() + re.sub('/*$', '', title) # [[/abc/////]] = [[/abc]]
            elif title.startswith('..'):
                linkparts = deque(title.split('/'))
                if len(linkparts) >= 2 and linkparts[-1] == '' and linkparts[-2] == '..': linkparts.pop()
                baseparts = page.title().split('/')
                try:
                    while linkparts:
                        if linkparts[0] == '..':
                            baseparts.pop()
                            linkparts.popleft()
                        else:
                            break
                except IndexError:
                    continue # invalid link
                if '..' in linkparts: continue # [[../a/../b]] will not produce a link.
                title = '/'.join(baseparts + list(linkparts))
                if not title: continue # empty string -> invalid link
            else:
                if '/../' in title: continue # [[abc/../def]] will not produce a link.
        if not page.site().isInterwikiLink(title):
            try:
                page = Page(page.site(), title)
                try:
                    hash(str(page))
                except Exception:
                    raise Error(u"Page %s contains invalid link to [[%s]]."
                                % (page.title(), title))
            except Error:
                if verbose:
                    output(u"Page %s contains invalid link to [[%s]]."
                           % (page.title(), title))
                continue
            if not withImageLinks and page.isImage():
                continue
            if page.sectionFreeTitle() and page not in result:
                result.append(page)
    return result

def linkedPages(self, withImageLinks=False):
    return extractLinkedPages(self.get(get_redirect=True), self, withImageLinks)

Page.linkedPages = linkedPages

"""
getRevision ============================================================
"""

def getRevision(self, revid):
    params = {
        'action'   : 'query',
        'prop'     : 'revisions',
        'revids'   : revid,
    }
    return Page(self, query.GetData(params, self)['query']['pages'].itervalues().next()['title'])
    
Site.getRevision = getRevision

"""
recentchanges ==========================================================
"""

def recentchanges(self, number=100, rcstart=None, rcend=None, rcshow=None,
                  rcdir='older', rctype='edit|new', namespace=None,
                  includeredirects=True, repeat=False, user=None,
                  returndict=False):
    if rctype is None:
        rctype = 'edit|new'
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
        data = query.GetData(params, self)
        if 'error' in data:
            raise RuntimeError('%s' % data['error'])
        try:
            rcData = data['query']['recentchanges']
        except KeyError:
            raise ServerError("The APIs don't return data, the site may be down")

        for i in rcData:
            if i['revid'] not in seen:
                seen.add(i['revid'])
                page = Page(self, i['title'], defaultNamespace=i['ns'])
                if 'comment' in i:
                    page._comment = i['comment']
                if returndict:
                    yield page, i
                else:
                    comment = u''
                    if 'comment' in i:
                        comment = i['comment']
                    yield page, i['timestamp'], i['newlen'], True, i['user'], comment
        if not repeat:
            break
        time.sleep(10)

Site.recentchanges = recentchanges

"""
QuickCntRev ============================================================
"""
def quickCntRev(self):
    params = {
        'action': 'query',
        'prop': 'revisions',
        'titles': self.title(),
        'rvprop': 'ids',
        'rvlimit': 5000,
    }
    cnt = 0
    while True:
        dat = query.GetData(params, site)
        cnt += len(dat['query']['pages'].itervalues().next()['revisions'])
        if 'query-continue' in dat:
            params['rvstartid'] = dat['query-continue']['revisions']['rvcontinue']
        else:
            break
    return cnt

Page.quickCntRev = quickCntRev

"""
getLang ================================================================
"""
def getLang(self, lang):
    for page in self.interwiki():
        if page.site().language() == lang:
            return page

Page.getLang = getLang

