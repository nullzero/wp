#-*-coding: utf-8 -*-

import utility
import sys, re, string, os
from pagegenerators import NewpagesPageGenerator
import wikipedia as pywikibot
import miscellaneous

env = utility.env

# constant
NUMOFNEWPAGE = 5
# end constant
    
def checkVandal(content):
    if(len(content) < 250): return True
    return False

if __name__ == "__main__":
    site = pywikibot.getSite()
    generator = NewpagesPageGenerator(number = NUMOFNEWPAGE)
    for page in generator:
        try:
            original_content = page.get()
        except pywikibot.NoPage:
            pywikibot.output(u'Page %s not found' % page.title())
            continue
        except pywikibot.IsRedirectPage:
            newpage = page.getRedirectTarget()
            pywikibot.output(u'Page %s redirects to \'%s\''
                             % (page.title(asLink=True), newpage.title()))
            generator.append(newpage)
            continue
        except pywikibot.SectionError:
            error("Page %s has no section %s"
                  % (page.title(), page.section()))
            continue

        clist = remove_wikicode(skip_section(original_content)).splitlines()
        content = u""
        for i in clist: content += i
        
        pywikibot.output(u"check " + page.title())
        
        if checkVandal(content):
            with open(os.path.join(env['WORKPATH'], 'av.reqdel'), "r") as f:
                lines = f.readlines()
            
            if page.title().encode("utf8") in lines: continue
            
            pywikibot.output(page.title() + u" is vandal!!")
            
            with open(os.path.join(env['WORKPATH'], 'av.reqdel'), "a") as f:
                f.write(page.title().encode("utf8"))
            
            page.put(u"{{ลบ|บอตแจ้งก่อกวนหรือไม่เป็นสารานุกรม}}\n" + original_content, 
            u"บอตแจ้งก่อกวนหรือไม่เป็นสาราฯ หากเกิดข้อผิดพลาด โปรดแจ้ง[[คุยกับผู้ใช้:Nullzero|ที่นี่]]")
