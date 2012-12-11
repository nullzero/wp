# -*- coding: utf-8  -*-

import re, sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try: import preload
except:
    print "Cannot import preload. Exit!"
    sys.exit()
    
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
        ([u"ละคร", u"ภาพยนตร์", u"ชื่อเรื่อง"], u"เรื่อง"),
        ([u"รับบท", u"บทบาท"], u"รับบทเป็น")]

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
            i = 0
            for line in lines:
                line = line.strip()
                if len(line) == 0: continue
                if len(line) == 1: raise Exception
                if(line[0:2] == u"|-"): continue
                if line[0] == u"!":
                    line = line[1:]
                    cells = line.split(u"!!")
                    for cell in cells:
                        cell = cell.strip()
                        result = p_wikilink.match(cell)
                        if result is not None: cell = result.group(1)
                        column.append(cell)
                        
                    startOperation = True
                    continue
                    
                if not startOperation: continue
                if line[0:2] == u"|}": break
                if line[0] == "|": line = line[1:]
                cells = line.split(u"||")
                j = 0
                for cell in cells:
                    text = cell.strip()
                    result = p_rowspan.search(text)
                    if result is not None:
                        rowspan = result.group(3)
                        for k in range(i + 1, i + int(rowspan)): lock[k][j] = True
                        
                    while lock[i][j]: j += 1
                    stable[i][j] = text
                    j += 1
                    
                i += 1
            
            n = i
            
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
            for i in keepcolumn: output += i[1] + u"!!"
            output = output[:-2] + u"\n"
            for i in range(n):
                output += u"|-\n"
                output += u"|"
                for j in range(len(keepcolumn)):
                    if stable[i][mark[j]] is not None:
                        output += stable[i][mark[j]] + u"||"
                
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
    pywikibot.output(u"'star-script' is invoked. (%s)" % preload.getTime())
    with open(QUEUE, "r") as f: content = f.read()
    with open(QUEUE, "w") as f: pass
    lines = content.splitlines()
    
    for i in lines:
        pywikibot.output(i)
        succ = dochange(i.decode("utf-8"))
        if not succ: 
            with open(NOTHING, "a") as f: f.write(i + "\n")
    
    pywikibot.output(u"'star-script' terminated. (%s)" % preload.getTime())    
    pywikibot.stopme()
