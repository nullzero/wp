# -*- coding: utf-8 -*-

import sys, os, re, time, traceback, urllib, subprocess, StringIO
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try: from lib import preload
except:
    print "เรียกใช้ไลบรารีไม่ได้ จบการทำงาน!"
    sys.exit()

import query, userlib
from lib import libdate, liblang, libstring, libgenerator, librevision, miscellaneous
import wikipedia as pywikibot

site = preload.site
env = preload.env
INF = 999999999

pageMain = pywikibot.Page(site, u"วิกิพีเดีย:ที่สุดในวิกิพีเดียภาษาไทย")
contentMain = pageMain.get()

def firstContributor(title):
    params = {
        'action': 'query',
        'prop': 'revisions',
        'titles': title,
        'rvprop': 'user',
        'rvlimit': 5000,
    }
    name = query.GetData(params, site)['query']['pages'].itervalues().next()['revisions'][-1]['user']
    if userlib.User(site, name).isAnonymous(): return u"-"
    return u"[[User:%s|%s]]" % (name, name)

def pagestat(): 
    '''
    allpages = []
    allpages.append((1, u"ครูพิเศษจอมป่วน รีบอร์น!"))
    allpages.append((2, u"ยกสยามปี 2"))
    allpages.append((3, u"ประเทศไทย"))
    allpages.append((4, u"อัจฉริยะข้ามคืน"))
    allpages.append((5, u"ระเบิดเถิดเทิง"))
    allpages.append((6, u"อภิสิทธิ์ เวชชาชีวะ"))
    allpages.append((7, u"สงครามโลกครั้งที่สอง"))
    allpages.append((8, u"พัดชา เอนกอายุวัฒน์"))
    allpages.append((9, u"ยกสยาม"))
    allpages.append((10, u"ทักษิณ ชินวัตร"))
    allpages.append((11, u"รายชื่อห้างสรรพสินค้าในประเทศไทย"))
    allpages.append((12, u"รายชื่อนวนิยายไทย"))
    allpages.append((13, u"รายชื่อการ์ตูนญี่ปุ่น"))
    allpages.append((14, u"รายชื่อตัวละครในดราก้อนบอล"))
    allpages.append((15, u"รายชื่อตัวละครในนินจาคาถาโอ้โฮเฮะ"))
    
    return sorted(allpages, key=lambda x: x[0], cmp=lambda a, b: b - a)
    '''
    allpages = []
    for page in site.allpages(includeredirects = False):
        print ">>>", page.title()
        params = {
            'action': 'query',
            'prop': 'revisions',
            'titles': page.title(),
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
        allpages.append((cnt, page.title()))
        
        if len(allpages) > 100000:
            allpages = sorted(allpages, key=lambda x: x[0], cmp=lambda a, b: b - a)
            del allpages[100000:]

    return sorted(allpages, key=lambda x: x[0], cmp=lambda a, b: b - a)

def getdat(title):
    s = re.search(u"<!-- เริ่มตาราง%s -->(.*?)<!-- จบตาราง%s -->" % 
        (title, title), contentMain, flags = re.DOTALL).group(1)
    s = [x.strip() for x in s.split(u"|-")]
    table = []
    for line in s:
        line = line.strip()
        if line.startswith(u"|}"): break
        if not line.startswith(u"|"): continue
        table.append([x.strip() for x in line.split(u"||")])
    
    for i in xrange(len(table)):
        table[i][0] = re.search(u"\[\[(.*?)\]\]", table[i][0]).group(1)
    
    return table

def tag(x):
    if x == 0: return u"{{คงที่}}"
    if x < 0: return u"{{ขึ้น}}"
    return u"{{ลง}}"

def writetable(table, title):
    global contentMain
    for i in xrange(len(table)):
        table[i][0] = u"%s %d. [[%s]]" % (tag(i + 1 - table[i][1]), i + 1, table[i][0])
        if table[i][1] == INF: table[i][1] = u"มาใหม่"
        table[i] = u" || ".join([unicode(x) for x in table[i]])
    contentMain = re.sub(u"(?<=<!-- เริ่มตาราง%s -->).*?(?=<!-- จบตาราง%s -->)" % 
        (title, title), u"".join(map(lambda x: u"\n|-\n| " + x, table)) + u"\n", contentMain, flags = re.DOTALL)

def flush():
    print contentMain
    return
    pageMain.put(contentMain, u"ปรับปรุงรายการ")

def getrankold(title, table):
    for i, val in enumerate(table):
        if val[0] == title:
            return i + 1
    return INF
    
def getconf(s):
    return re.search(u"<!-- %s \{(.*?)\} -->" % s, contentMain).group(1)

def main():
    """
    most edits
    """
    allpages = pagestat()
    oldtable = getdat(u"บทความแก้ไขมากสุด")
    oldtablelist = getdat(u"บทความรายชื่อแก้ไขมากสุด")
    table = []
    tablelist = []
    ptr = 0
    while True:
        if (len(tablelist) < 5) and (u"รายชื่อ" in allpages[ptr][1]):
            rankold = getrankold(allpages[ptr][1], oldtablelist)
            tablelist.append([allpages[ptr][1], rankold, allpages[ptr][0], firstContributor(allpages[ptr][1])])
            ptr += 1
        elif len(table) < 10:
            rankold = getrankold(allpages[ptr][1], oldtable)
            table.append([allpages[ptr][1], rankold, allpages[ptr][0], firstContributor(allpages[ptr][1])])
            ptr += 1
        else:
            break
            
    writetable(table, u"บทความแก้ไขมากสุด")
    writetable(tablelist, u"บทความรายชื่อแก้ไขมากสุด")
    """
    long pages
    """
    table = []
    oldlongpages = getdat(u"บทความยาวสุด")
    for page, length in site.longpages(5):
        table.append([page.title(), getrankold(page.title(), oldlongpages), length])
    writetable(table, u"บทความยาวสุด")
    flush()
    '''
    """
    most edits (user)
    """
    oldusers = getdat(u"ชาววิกิพีเดียที่เขียนมากที่สุด")
    limit = getconf(u"ตารางชาววิกิพีเดียที่เขียนมากที่สุด")
    table = []
    for line in pywikibot.Page(site, u"วิกิพีเดีย:รายชื่อชาววิกิพีเดียที่แก้ไขมากที่สุด_500_อันดับ").get().split('\n'):
        libe = line.strip()
        if line == u"|-": continue
        if line.startswith(u"|"):
            line = [x.strip() for x in line.split(u"||")]
            name = re.search(u"\[\[(.*?)\]\]", line[1]).group(1)
            cnt = re.search(u"\|(\d+)\]\]", line[2]).group(1)
            if int(cnt) < int(limit): break
            table.append([name, getrankold(name, oldusers), cnt])
    writetable(table, u"ชาววิกิพีเดียที่เขียนมากที่สุด")
    flush()
    '''
main()
