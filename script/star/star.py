# -*- coding: utf-8 -*-

import re, sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try: from lib import preload
except:
    print "Cannot import preload. Exit!"
    sys.exit()

from lib import libdate    
import wikipedia as pywikibot

MAXN = 500
QUEUE = os.path.abspath(os.path.join(os.path.dirname(__file__), "star.fqueue"))
NOTHING = os.path.abspath(os.path.join(os.path.dirname(__file__), "star.fnothing"))

site = pywikibot.getSite()

def dochange(pagename):
    page = pywikibot.Page(site, pagename)
    original_content = page.get()
    content = original_content

    p_wikitable = re.compile(u"\{\|.*?wikitable.*?\|\}", re.DOTALL)
    p_rowspan = re.compile(u"rowspan(\ )*=(\ )*\"(.*?)\"")
    p_wikilink = re.compile(u"\[\[(.*?)\]\]")
    tablelist = p_wikitable.findall(content)
    
    keepcolumn = [([u"พ.ศ.", u"ปี"], u"ปี พ.ศ."), 
        ([u"ชื่อละคร", u"ละคร", u"ภาพยนตร์", u"ชื่อเรื่อง", u"ละครเวที"], u"เรื่อง"),
        ([u"รับบท", u"บทบาท"], u"รับบทเป็น"),
        ([u"หมายเหตุและรางวัล"], u"หมายเหตุ"),
    ]
    
    for table in tablelist:
        try:
            column = []
            stable = [[None for i in range(MAXN)] for j in range(MAXN)]
            lock = [[False for i in range(MAXN)] for j in range(MAXN)]
            mark = [0 for i in range(MAXN)]
            skipThisTable = False
            startOperation = False
            pre, post = content.split(table)
            
            lines = table.splitlines()
            for i in xrange(len(lines)):
                if lines[i].strip().startswith(u"|-"):
                    lines[i] = u"|-"
                    
            table = u"\n".join(lines)
            table = table.replace(u"||", u"\n|")
            table = table.replace(u"!!", u"\n!")
            lines = table.splitlines()
            i, j = -1, 0
            for line in lines:
                line = line.strip()
                if line.startswith(u"|-"):
                    if startOperation:
                        i += 1
                        j = 0
                elif line.startswith(u"|}"):
                    break
                elif line.startswith(u"!"):
                    startOperation = True
                    column.append(p_wikilink.sub("\g<1>", line[1:].strip()))
                elif line.startswith(u"|"):
                    while lock[i][j]: j += 1
                    
                    text = line[1:].strip()
                    result = p_rowspan.search(text)
                    if result is not None:
                        rowspan = result.group(3)
                        for k in xrange(i + 1, i + int(rowspan)):
                            lock[k][j] = True
                            
                    stable[i][j] = text
                    j += 1
                    
            n = i + 1
            
            for idx, val in enumerate(keepcolumn):
                vlist, vstr = val
                found = False
                for idx2, val2 in enumerate(column):
                    if (val2 == vstr) or (val2 in vlist):
                        mark[idx] = idx2
                        found = True
                        break
                        
                if not found:
                    skipThisTable = True
                    break
                    
            if skipThisTable:
                pywikibot.output(u"skip " + page.title())
                continue
                    
            output = u'{| class="wikitable"\n|-\n!'
            for i in keepcolumn: output += i[1] + u" !!"
            output = output[:-2] + u"\n"
            for i in xrange(n):
                output += u"|-\n"
                output += u"|"
                for j in xrange(len(keepcolumn)):
                    if stable[i][mark[j]] is not None:
                        output += stable[i][mark[j]] + u" ||"
                
                output = output[:-2] + u"\n"
            output += u"|}"
            content = pre + output + post
        except: pass
    
    if content == original_content:
        pywikibot.output("Nothing to do!")
        return False
        
    page.put(content, u"ลบตาม[[วิกิพีเดีย:โครงการวิกิภาพยนตร์/รูปแบบการเขียน/บทความนักแสดง]]")
    return True

if __name__ == "__main__":
    pywikibot.handleArgs(u"-log")
    pywikibot.output(u"'star-script' is invoked. (%s)" % libdate.getTime())
    with open(QUEUE, "r") as f: content = f.read()
    with open(QUEUE, "w") as f: pass
    lines = content.splitlines()
    #lines = ["รัฐภูมิ_โตคงทรัพย์"]
    
    for i in lines:
        pywikibot.output(i)
        succ = dochange(i.decode("utf-8"))
        if not succ: 
            with open(NOTHING, "a") as f: f.write(i + "\n")
    
    pywikibot.output(u"'star-script' terminated. (%s)" % libdate.getTime())    
    pywikibot.stopme()
