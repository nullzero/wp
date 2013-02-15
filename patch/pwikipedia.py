# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try: from lib import preload
except:
    print "เรียกใช้ไลบรารีไม่ได้ จบการทำงาน!"
    sys.exit()
    
from wikipedia import *

def linkedPages(self, withImageLinks=False):
    return extractLinkedPages(self.get(get_redirect=True), self, withImageLinks)

def getRevision(self, revid):
    params = {
        'action'   : 'query',
        'prop'     : 'revisions',
        'revids'   : revid,
    }
    return Page(self, query.GetData(params, self)['query']['pages'].itervalues().next()['title'])

Page.linkedPages = linkedPages
Site.getRevision = getRevision

def extractLinkedPages(content, page, withImageLinks=False):
    """Return a list of Pages that this Page links to.

    Only returns pages from "normal" internal links. Category links are
    omitted unless prefixed with ":". Image links are omitted when parameter
    withImageLinks is False. Embedded templates are omitted (but links
    within them are returned). All interwiki and external links are omitted.

    @param withImageLinks: include Image links
    @return: a list of Page objects.
    """
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
