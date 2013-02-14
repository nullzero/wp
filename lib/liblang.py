# -*- coding: utf-8  -*-

import re, sys

try: import preload
except:
    print "เรียกใช้ไลบรารีไม่ได้ จบการทำงาน!"
    sys.exit()
    
import libstring, movepages
import wikipedia as pywikibot

ThaiBegin = u"\u0e01"
ThaiEnd = u"\u0e5b"

Thai = {
    'Alphabet' : u"".join([unichr(i) for i in xrange(ord(u'ก'), ord(u'ฮ') + 1)]),
    'VowelFront' : u"เแโใไ",
    'VowelBack' : u"ะาๅ",
    'VowelUm' : u"ำ",
    'VowelUp' : u"ัิีึืํ",
    'VowelDown' : u"ฺุู",
    'VowelTaiku' : u"็",
    'Sound' : u"่้๊๋",
    'Tantakad' : u"์",
    'Paiyan' : u"ฯ",
    'Yamok' : u"ๆ",
}

Thai['All'] = u"".join([Thai[i] for i in Thai])
Thai['Not'] = u"^%s" % Thai['All']

ASCII = {
    'Symbol' : u"".join([unichr(i) for i in xrange(128) if (re.search(u"[A-Za-z]", unichr(i)) is None)]),
}

def analyzeChar(content):
    cntThaiChar = 0
    cntForeignChar = 0
    
    for i in content:
        if i in Thai['All']: cntThaiChar += 1
        else: cntForeignChar += 1
    
    return cntThaiChar, cntForeignChar

def bracket(x): return u"[" + x + u"]"

def cntWrongVowel(line):
    cnt = 0
    cnt += libstring.findOverlap(bracket(Thai['VowelFront']) + bracket(Thai['VowelFront']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelFront']) + bracket(Thai['VowelBack']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelFront']) + bracket(Thai['VowelUm']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelFront']) + bracket(Thai['VowelUp']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelFront']) + bracket(Thai['VowelDown']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelFront']) + bracket(Thai['VowelTaiku']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelFront']) + bracket(Thai['Sound']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelFront']) + bracket(Thai['Tantakad']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelFront']) + bracket(Thai['Paiyan']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelFront']) + bracket(Thai['Yamok']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelFront']) + bracket(Thai['Not']), line)
               
    cnt += libstring.findOverlap(bracket(Thai['VowelBack']) + bracket(Thai['VowelUm']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelBack']) + bracket(Thai['VowelUp']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelBack']) + bracket(Thai['VowelDown']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelBack']) + bracket(Thai['VowelTaiku']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelBack']) + bracket(Thai['Sound']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelBack']) + bracket(Thai['Tantakad']), line)
               
    cnt += libstring.findOverlap(bracket(Thai['VowelUm']) + bracket(Thai['VowelBack']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelUm']) + bracket(Thai['VowelUm']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelUm']) + bracket(Thai['VowelUp']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelUm']) + bracket(Thai['VowelDown']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelUm']) + bracket(Thai['VowelTaiku']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelUm']) + bracket(Thai['Sound']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelUm']) + bracket(Thai['Tantakad']), line)
               
    cnt += libstring.findOverlap(bracket(Thai['VowelUp']) + bracket(Thai['VowelBack']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelUp']) + bracket(Thai['VowelUm']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelUp']) + bracket(Thai['VowelUp']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelUp']) + bracket(Thai['VowelDown']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelUp']) + bracket(Thai['VowelTaiku']), line)
               
    cnt += libstring.findOverlap(bracket(Thai['VowelDown']) + bracket(Thai['VowelBack']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelDown']) + bracket(Thai['VowelUm']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelDown']) + bracket(Thai['VowelUp']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelDown']) + bracket(Thai['VowelDown']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelDown']) + bracket(Thai['VowelTaiku']), line)
               
    cnt += libstring.findOverlap(bracket(Thai['VowelTaiku']) + bracket(Thai['VowelBack']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelTaiku']) + bracket(Thai['VowelUm']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelTaiku']) + bracket(Thai['VowelUp']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelTaiku']) + bracket(Thai['VowelDown']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelTaiku']) + bracket(Thai['VowelTaiku']), line)
    cnt += libstring.findOverlap(bracket(Thai['VowelTaiku']) + bracket(Thai['Tantakad']), line)
               
    cnt += libstring.findOverlap(bracket(Thai['Sound']) + bracket(Thai['VowelUp']), line)
    cnt += libstring.findOverlap(bracket(Thai['Sound']) + bracket(Thai['VowelDown']), line)
    cnt += libstring.findOverlap(bracket(Thai['Sound']) + bracket(Thai['VowelTaiku']), line)
    cnt += libstring.findOverlap(bracket(Thai['Sound']) + bracket(Thai['Sound']), line)
    cnt += libstring.findOverlap(bracket(Thai['Sound']) + bracket(Thai['Tantakad']), line)
               
    cnt += libstring.findOverlap(bracket(Thai['Tantakad']) + bracket(Thai['VowelBack']), line)
    cnt += libstring.findOverlap(bracket(Thai['Tantakad']) + bracket(Thai['VowelUm']), line)
    cnt += libstring.findOverlap(bracket(Thai['Tantakad']) + bracket(Thai['VowelUp']), line)
    cnt += libstring.findOverlap(bracket(Thai['Tantakad']) + bracket(Thai['VowelDown']), line)
    cnt += libstring.findOverlap(bracket(Thai['Tantakad']) + bracket(Thai['VowelTaiku']), line)
    cnt += libstring.findOverlap(bracket(Thai['Tantakad']) + bracket(Thai['Sound']), line)
    cnt += libstring.findOverlap(bracket(Thai['Tantakad']) + bracket(Thai['Tantakad']), line)
               
    cnt += libstring.findOverlap(bracket(Thai['Paiyan']) + bracket(Thai['VowelBack']), line)
    cnt += libstring.findOverlap(bracket(Thai['Paiyan']) + bracket(Thai['VowelUm']), line)
    cnt += libstring.findOverlap(bracket(Thai['Paiyan']) + bracket(Thai['VowelUp']), line)
    cnt += libstring.findOverlap(bracket(Thai['Paiyan']) + bracket(Thai['VowelDown']), line)
    cnt += libstring.findOverlap(bracket(Thai['Paiyan']) + bracket(Thai['VowelTaiku']), line)
    cnt += libstring.findOverlap(bracket(Thai['Paiyan']) + bracket(Thai['Sound']), line)
    cnt += libstring.findOverlap(bracket(Thai['Paiyan']) + bracket(Thai['Tantakad']), line)
    cnt += libstring.findOverlap(bracket(Thai['Paiyan']) + bracket(Thai['Paiyan']), line)
    cnt += libstring.findOverlap(bracket(Thai['Paiyan']) + bracket(Thai['Yamok']), line)
               
    cnt += libstring.findOverlap(bracket(Thai['Yamok']) + bracket(Thai['VowelFront']), line)
    cnt += libstring.findOverlap(bracket(Thai['Yamok']) + bracket(Thai['VowelBack']), line)
    cnt += libstring.findOverlap(bracket(Thai['Yamok']) + bracket(Thai['VowelUm']), line)
    cnt += libstring.findOverlap(bracket(Thai['Yamok']) + bracket(Thai['VowelUp']), line)
    cnt += libstring.findOverlap(bracket(Thai['Yamok']) + bracket(Thai['VowelDown']), line)
    cnt += libstring.findOverlap(bracket(Thai['Yamok']) + bracket(Thai['VowelTaiku']), line)
    cnt += libstring.findOverlap(bracket(Thai['Yamok']) + bracket(Thai['Sound']), line)
    cnt += libstring.findOverlap(bracket(Thai['Yamok']) + bracket(Thai['Tantakad']), line)
    cnt += libstring.findOverlap(bracket(Thai['Yamok']) + bracket(Thai['Paiyan']), line)                
               
    cnt += libstring.findOverlap(bracket(Thai['Not']) + bracket(Thai['VowelBack']), line)
    cnt += libstring.findOverlap(bracket(Thai['Not']) + bracket(Thai['VowelUm']), line)
    cnt += libstring.findOverlap(bracket(Thai['Not']) + bracket(Thai['VowelUp']), line)
    cnt += libstring.findOverlap(bracket(Thai['Not']) + bracket(Thai['VowelDown']), line)
    cnt += libstring.findOverlap(bracket(Thai['Not']) + bracket(Thai['VowelTaiku']), line)
    cnt += libstring.findOverlap(bracket(Thai['Not']) + bracket(Thai['Sound']), line)
    cnt += libstring.findOverlap(bracket(Thai['Not']) + bracket(Thai['Tantakad']), line)
    
    return cnt

checkVowel = u"แโใไะาๅำัิีึืํฺุู็่้๊๋์ฯ"

def fixRepetedVowelTitle(page):
    opagetitle = page.title()
    pagetitle = opagetitle
    
    for i in checkVowel: pagetitle = re.sub(i + u"+", i, pagetitle)
    
    if pagetitle != opagetitle:
        pywikibot.output("ย้ายบทความชื่อมีสระซ้อน")
        try: 
            movepages.MovePagesBot(None, None, True, False, True, u"โรบอต: เปลี่ยนชื่อบทความมีสระซ้อน").moveOne(page, pagetitle)
            pywikibot.Page(pywikibot.getSite(), opagetitle).put(u"{{ลบ|ชื่อมีสระซ้อน ย้ายหน้าไป[[%s]]แล้ว}}" % pagetitle, u"โรบอต: แจ้งลบชื่อมีสระซ้อน", force = True)
        except: preload.error()
    
def fixRepetedVowel(content):
    for i in checkVowel: content = re.sub(i + u"+", i, content)
    return content

import random
from subprocess import Popen, PIPE, STDOUT

def randomCheckRepetition(s):
    s = s.encode("utf-8")
    s = re.sub("", "\n", re.sub("\n", "", s))
    size = len(s)
    begin = random.randint(0, max(0, size - 700 * 2))
    end = min(begin + 700 * 2, size)
    if len(s[begin:end]) == 0: return 0
    p = Popen([preload.File(__file__, "rle2")], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    output = p.communicate(input=s[begin:end])[0]
    return int(output)

def checkRepetition(s):
    return (randomCheckRepetition(s) + randomCheckRepetition(s) + randomCheckRepetition(s)) / 3
