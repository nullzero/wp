#-*-coding: utf-8 -*-

import utility
import sys, re, string, os
from pagegenerators import NewpagesPageGenerator
from userlib import User
import wikipedia as pywikibot
from miscellaneous import remove_wikicode, skip_section

env = utility.env

NUMOFNEWPAGE = 2
CHECKEDFILE = os.path.join(env['WORKPATH'], 'av.checked')
GOODMANFILE = os.path.join(env['WORKPATH'], 'av.goodman')

# predefine
def getContent(page, generator):
    try:
        content = page.get()
    except pywikibot.NoPage:
        pywikibot.output(u'Page %s not found' % page.title())
        return None
    except pywikibot.IsRedirectPage:
        newpage = page.getRedirectTarget()
        pywikibot.output(u'Page %s redirects to \'%s\''
                         % (page.title(asLink=True), newpage.title()))
        generator.append(newpage)
        return None
    except pywikibot.SectionError:
        error("Page %s has no section %s"
              % (page.title(), page.section()))
        return None
        
    return content

def readfile(filename):
    with open(filename, "r") as f:
        content = f.read()
    
    return content.splitlines()

def MyNewpagesPageGenerator(number=100, repeat=False, site=None, namespace=0, user=None):
    """
    Iterate Page objects for all new titles in a single namespace.
    """
    # defaults to namespace 0 because that's how Special:Newpages defaults
    site = pywikibot.getSite()
    gen = site.recentchanges(number=number, rcshow=['!redirect'], rctype='new',
                                     namespace=namespace, repeat=repeat,
                                     user=user, returndict=True)
                                     
    for newpage, pageitem in gen:
        yield (newpage, pageitem['user'])
# end predefine

def reqDelete(page, reason, original_content):
    page.put(u"{{ลบ|" + reason + u"}}\n" + original_content, 
            u"บอตแจ้ง" + reason + u" หากเกิดข้อผิดพลาด โปรดแจ้ง[[คุยกับผู้ใช้:Nullzero|ที่นี่]]")

if __name__ == "__main__":
    site = pywikibot.getSite()
    generator = MyNewpagesPageGenerator(number = NUMOFNEWPAGE)
    
    checkedList = readfile(CHECKEDFILE)
    goodManList = readfile(GOODMANFILE)
    
    for page, username in generator:
        pywikibot.output(u"I am checking " + page.title() + u" by user " + username)
        
        """
        if page.title().encode("utf8") in checkedList:
            print page.title().encode("utf8")
            pywikibot.output(u"Skip! I have already checked.")
            break
        """
        
        # {{done}}
        with open(os.path.join(env['WORKPATH'], CHECKEDFILE), "a") as f:
                f.write(page.title().encode("utf8") + '\n')
        
        # {{done}}
        if username.encode("utf8") in goodManList:
            pywikibot.output(u"Skip! Good man writes it.")
            continue
        
        # {{done}}
        userobject = User(site, username)
        if userobject.isRegistered() and 'sysop' in userobject.groups():
            pywikibot.output(u"Skip! Admin writes it.")
            continue
        
        # {{done}}
        original_content = getContent(page, generator)
        if original_content is None:
            pywikibot.output(u"Skip! There is an error")
            continue
            
        # {{done}}
        pat_skip = re.compile(u"\{\{(\ )*(ลบ|delete|สั้นมาก|ละเมิดลิขสิทธิ์).*?\}\}")
        if pat_skip.search(original_content) is not None:
            pywikibot.output(u"Skip! This is a legal article")
            continue
            
        # {{done}}
        if len(original_content) < 200:
            pywikibot.output(u"Vandal! too few length of content")
            reqDelete(page, u"ไม่เป็นสารานุกรม", original_content)
            continue
        
        content = remove_wikicode(skip_section(original_content))
        clist = content.splitlines()
        content = u""
        for i in clist: content += i
        
        # {{done}}
        if abs(len(content) - len(original_content)) < 10:
            pywikibot.output(u"Vandal! too few length of markup")
            reqDelete(page, u"ไม่เป็นสารานุกรม", original_content)
            continue
        
        pat_resume = re.compile(u".*เกิด.*วันที่.*(จบ|เรียน|ศึกษา).*")
        
        if pat_resume.match(content) is not None:
            pywikibot.output(u"Resume")
            reqDelete(page, u"ประวัติส่วนตัวไม่โดดเด่น", original_content)
        
        # {{done}}
        if original_content[0] == u" " and original_content[1] == u" ":
            pywikibot.output(u"Violate copyright policy!")
            reqDelete(page, u"ไม่เป็นสาราฯ/ละเมิดลิขสิทธิ์", original_content)