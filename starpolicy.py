# -*- coding: utf-8  -*-

try: import utility
except: pass

import re
import wikipedia as pywikibot

MAXN = 200
site = pywikibot.getSite()

def dochange(pagename):
    page = pywikibot.Page(site, pagename)
    content = page.get()

    p_wikitable = re.compile(u"\{\|.*?wikitable.*?\|\}", re.DOTALL)
    p_rowspan = re.compile(u"rowspan(\ )*=(\ )*\"(.*?)\"")
    p_interwiki = re.compile(u"\[\[(.*?)\]\]")
    tablelist = p_wikitable.findall(content)

    #keepcolumn = [u"ปี พ.ศ.", u"เรื่อง", u"รับบทเป็น"]
    #keepcolumn = [u"ปี", u"ละคร", u"รับบทเป็น"]
    #keepcolumn = [u"เรื่อง", u"รับบทเป็น"]
    keepcolumn = [u"เรื่อง", u"รับบท"]
    #keepcolumn = [u"ปี พ.ศ.", u"เรื่อง"]

    for table in tablelist:
        column = []
        stable = [[None for i in range(MAXN)] for j in range(MAXN)]
        lock = [[False for i in range(MAXN)] for j in range(MAXN)]
        mark = [0 for i in range(MAXN)]
        skipThisTable = False
        pre, post = content.split(table)
        startOperation = False
        lines = table.splitlines()
        i = 0
        j = 0
        for line in lines:
            line = line.strip()
            if len(line) == 0: continue
            if(line[0:2] == u"|-"): continue
            if line[0] == u"!":
                line = line[1:]
                cells = line.split(u"!!")
                for cell in cells:
                    cell = cell.strip()
                    result = p_interwiki.match(cell)
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
            found = False
            for idx2, val2 in enumerate(column):
                if val == val2:
                    mark[idx] = idx2
                    found = True
                    break
                    
            if not found:
                skipThisTable = True
                break
                
        if skipThisTable:
            pywikibot.output(u"skip " + page.title())
            continue
                
        output = u'{| class="wikitable"\n!'
        for i in keepcolumn: output += i + u"!!"
        output = output[:-2] + u"\n"
        for i in range(n):
            output += u"|-\n"
            output += u"|"
            for j in range(len(keepcolumn)):
                if stable[i][mark[j]] is not None:
                    output += stable[i][mark[j]] + u"||"
            
            output = output[:-2] + u"\n"
        output += u"|}\n"
        content = pre + output + post
    
    page.put(content, u"ลบตาม[[วิกิพีเดีย:โครงการวิกิภาพยนตร์/รูปแบบการเขียน/บทความนักแสดง]]")
    
arr = [u"ชาลิดา_วิจิตรวงศ์ทอง"]
for i in arr: dochange(i)
pywikibot.stopme()
