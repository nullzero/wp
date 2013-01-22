# -*- coding: utf-8 -*-

import re, sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try: from lib import preload
except:
    print "Cannot import preload. Exit!"
    sys.exit()

from lib import libdate, libcleaner, libgenerator
import wikipedia as pywikibot

MAXN = 500
QUEUE = os.path.abspath(os.path.join(os.path.dirname(__file__), "star.fqueue"))
NOTHING = os.path.abspath(os.path.join(os.path.dirname(__file__), "star.fnothing"))

site = pywikibot.getSite()

const = {
    'strict' : 1,
    'nstrict' : 2,
}

def extractHeader(s):
    s = s.strip()
    res = re.search("\|(.*)", s)
    if res is not None: s = res.group(1).strip()
    res = re.search("\[\[(.*?)\]\]", s)
    if res is not None: s = res.group(1).strip()
    return s

def dochange(original_content):
    content = original_content

    p_wikitable = re.compile(u"\{\|.*?wikitable.*?\|\}", re.DOTALL)
    p_rowspan = re.compile(u"rowspan(\ )*=(\ )*\"(.*?)\"")
    tablelist = p_wikitable.findall(content)
    
    keepcolumn = [([u"พ.ศ.", u"ปี", "ปีที่แสดง"], u"ปี พ.ศ.", const['strict']), 
        ([u"ชื่อละคร", u"ละคร", u"ภาพยนตร์", u"ชื่อเรื่อง", u"ละครเวที", u"ภาพยนตร์เรื่อง", u"ละครเรื่อง"], u"เรื่อง", const['strict']),
        ([u"รับบท", u"บทบาท", u"บท", u"แสดงเป็น"], u"รับบทเป็น", const['strict']),
        ([u"หมายเหตุและรางวัล"], u"หมายเหตุ", const['nstrict']),
    ]
    
    for table in tablelist:
        try:
            column = []
            stable = [[None for i in range(MAXN)] for j in range(MAXN)]
            lock = [[False for i in range(MAXN)] for j in range(MAXN)]
            mark = [None for i in range(MAXN)]
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
                    column.append(extractHeader(line[1:]))
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
            cntfound = 0
            for idx, val in enumerate(keepcolumn):
                vlist, vstr, vstrict = val
                found = False
                for idx2, val2 in enumerate(column):
                    if (val2 == vstr) or (val2 in vlist):
                        mark[idx] = idx2
                        found = True
                        cntfound += 1
                        break
                        
                if (not found) and (vstrict == const['strict']):
                    skipThisTable = True
                    break
            
            if (skipThisTable) or (cntfound == len(column)):
                pywikibot.output(u"skip " + page.title())
                continue
                    
            output = u'{| class="wikitable"\n|-\n! '
            for i in xrange(len(keepcolumn)):
                if mark[i] is not None: output += keepcolumn[i][1] + u" !!"
            output = output[:-2] + u"\n"
            for i in xrange(n):
                output += u"|-\n"
                output += u"| "
                for j in xrange(len(keepcolumn)):
                    if (mark[j] is not None) and (stable[i][mark[j]] is not None):
                        output += stable[i][mark[j]] + u" ||"
                if output != u"": output = output[:-3] + u"\n"
            output += u"|}"
            
            content = pre + output + post
        except: preload.error()
    
    if content == original_content: return
    
    content = libcleaner.clean(content)
    return content

if __name__ == "__main__":
    pywikibot.handleArgs(u"-log")
    
    if len(sys.argv) > 1:
        pagename = sys.argv[1]
        gen = [pywikibot.Page(pywikibot.getSite(), pagename.decode("utf-8"))]
    else:
        gen = libgenerator.CatGenerator(u"นักแสดงไทย")
    
    always = False
    
    for page in gen:
        pywikibot.output(page.title())
        try:
            ocontent = page.get()
        except:
            preload.error()
            continue
            
        content = dochange(ocontent)
        
        if (content is not None) and (ocontent != content):
            pywikibot.showDiff(ocontent, content)
            if not always: choice = raw_input()
            if choice == 'n': continue
            if choice == 'a': always = True
            page.put(content, u"ลบตาม[[วิกิพีเดีย:โครงการวิกิภาพยนตร์/รูปแบบการเขียน/บทความนักแสดง]]", force = True)
    
    pywikibot.stopme()
