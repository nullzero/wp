#-*-coding: utf-8 -*-

import utility
import sys, urllib2, urllib, re, string, os
from pagegenerators import NewpagesPageGenerator
from BeautifulSoup import BeautifulSoup
from random import randint
import wikipedia as pywikibot

env = utility.env
# predefine

EXCLUDEQUOTE = True

wikipedia_names = {
    '--': u'Wikipedia',
    'am': u'ዊኪፔድያ',
    'an': u'Biquipedia',
    'ang': u'Wicipǣdia',
    'ar': u'ويكيبيديا',
    'arc': u'ܘܝܟܝܦܕܝܐ',
    'ast': u'Uiquipedia',
    'az': u'Vikipediya',
    'bat-smg': u'Vikipedėjė',
    'be': u'Вікіпэдыя',
    'be-x-old': u'Вікіпэдыя',
    'bg': u'Уикипедия',
    'bn': u'উইকিপিডিয়া',
    'bpy': u'উইকিপিডিয়া',
    'ca': u'Viquipèdia',
    'ceb': u'Wikipedya',
    'chr': u'ᏫᎩᏇᏗᏯ',
    'cr': u'ᐎᑭᐱᑎᔭ',
    'cs': u'Wikipedie',
    'csb': u'Wikipedijô',
    'cu': u'Википедї',
    'cv': u'Википеди',
    'cy': u'Wicipedia',
    'diq': u'Wikipediya',
    'dv': u'ވިކިޕީޑިއާ',
    'el': u'Βικιπαίδεια',
    'eo': u'Vikipedio',
    'et': u'Vikipeedia',
    'fa': u'ویکی‌پدیا',
    'fiu-vro': u'Vikipeediä',
    'fr': u'Wikipédia',
    'frp': u'Vuiquipèdia',
    'fur': u'Vichipedie',
    'fy': u'Wikipedy',
    'ga': u'Vicipéid',
    'gu': u'વિકિપીડિયા',
    'he': u'ויקיפדיה',
    'hi': u'विकिपीडिया',
    'hr': u'Wikipedija',
    'hsb': u'Wikipedija',
    'hu': u'Wikipédia',
    'hy': u'Վիքիփեդիա',
    'io': u'Wikipedio',
    'iu': u'ᐅᐃᑭᐱᑎᐊ/oikipitia',
    'ja': u'ウィキペディア',
    'jbo': u'uikipedias',
    'ka': u'ვიკიპედია',
    'kk': u'Уикипедия',
    'kn': u'ವಿಕಿಪೀಡಿಯ',
    'ko': u'위키백과',
    'ksh': u'Wikkipedija',
    'la': u'Vicipaedia',
    'lad': u'ויקיפידיה',
    'lt': u'Vikipedija',
    'lv': u'Vikipēdija',
    'mk': u'Википедија',
    'ml': u'വിക്കിപീഡിയ',
    'mo': u'Википедия',
    'mr': u'विकिपिडीया',
    'mt': u'Wikipedija',
    'nah': u'Huiquipedia',
    'ne': u'विकिपीडिया',
    'nrm': u'Viqùipédie',
    'oc': u'Wikipèdia',
    'os': u'Википеди',
    'pa': u'ਵਿਕਿਪੀਡਿਆ',
    'pt': u'Wikipédia',
    'qu': u'Wikipidiya',
    'rmy': u'Vikipidiya',
    'ru': u'Википедия',
    'sco': u'Wikipaedia',
    'si': u'විකිපීඩියා',
    'sk': u'Wikipédia',
    'sl': u'Wikipedija',
    'sr': u'Википедија',
    'su': u'Wikipédia',
    'ta': u'விக்கிபீடியா',
    'tg': u'Википедиа',
    'th': u'วิกิพีเดีย',
    'tr': u'Vikipedi',
    'uk': u'Вікіпедія',
    'uz': u'Vikipediya',
    'yi': u'‫װיקיפעדיע',
    'zh': u'维基百科',
    'zh-classical': u'維基大典',
    'zh-yue': u'維基百科',
}

editsection_names = {
    'ar': u'\[عدل\]',
    'en': u'\[edit\]',
    'fa': u'\[ویرایش\]',
    'fr': u'\[modifier\]',
    'de': u'\[Bearbeiten\]',
    'es,pt': u'\[editar\]',
    'it': u'\[modifica\]',
    'is': u'\[breyti\]',
    'ja': u'\[編集\]',
    'zh': u'\[编辑\]',
}

sections_to_skip = {
    'ar': [u'مراجع', u'قراءة أخرى', u'ملاحظات', u'وصلات خارجية'],
    'en': [u'References', u'Further reading', u'Citations', u'External links'],
    'fa': [u'منابع', u'منابع برای مطالعه بیشتر', u'یادکردها',
           u'پیوند به بیرون'],
    'es': [u'Referencias', u'Ver también', u'Bibliografía', u'Enlaces externos',
           u'Notas'],
    'fr': [u'Liens externes'],
    'it': [u'Bibliografia', u'Discografia', u'Opere bibliografiche',
           u'Riferimenti bibliografici', u'Collegamenti esterni',
           u'Pubblicazioni', u'Pubblicazioni principali',
           u'Bibliografia parziale'],
    'is': [u'Heimildir', u'Tenglar', u'Tengt efni'], 
    'ja': [u'脚注', u'脚注欄', u'脚注・出典', u'出典', u'注釈'],
    'zh': [u'參考文獻', u'参考文献', u'參考資料', u'参考资料', u'資料來源', u'资料来源',
           u'參見', u'参见', u'參閱', u'参阅'],
    'th': [u'อ้างอิง', u'ดูเพิ่มเติม']
}


def join_family_data(reString, namespace):
    for s in pywikibot.Family().namespaces[namespace].itervalues():
        if type (s) == list:
            for e in s:
                reString += '|' + e
        else:
            reString += '|' + s
    return '\s*(' + reString + ')\s*'
    
reImageC = re.compile('\[\[' + join_family_data('Image', 6) + ':.*?\]\]', re.I)
reWikipediaC = re.compile('(' + '|'.join(wikipedia_names.values()) + ')', re.I)
reSectionNamesC = re.compile('(' + '|'.join(editsection_names.values()) + ')')

def remove_wikicode(text, re_dotall = True, remove_quote = EXCLUDEQUOTE, debug = False):
    if not text:
        return ""

    if debug:
        write_log(text+'\n', "copyright/wikicode.txt")

    text = re.sub('(?i)</?(p|u|i|b|em|div|span|font|small|big|code|tt).*?>', '', text)
    text = re.sub('(?i)<(/\s*)?br(\s*/)?>', '', text)
    text = re.sub('<!--.*?-->', '', text)

    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')

    # remove URL
    text = re.sub('(ftp|https?)://[\w/.,;:@&=%#\\\?_!~*\'|()\"+-]+', ' ', text)

    # remove Image tags
    text = reImageC.sub("", text)

    # replace piped wikilink
    text = re.sub("\[\[[^\]]*?\|(.*?)\]\]", "\\1", text)

    # remove unicode and polytonic template
    text = re.sub("(?i){{(unicode|polytonic)\|(.*?)}}", "\\1", text)

    if re_dotall:
       flags = "(?xsim)"
       # exclude wikitable
       text = re.sub('(?s){\|.*?^\|}', '', text)
    else:
       flags = "(?xim)"

    text = re.sub("""
    %s
    (
        <ref[^>]*?\s*/\s*>     | # exclude <ref name = '' / > tags
        <ref.*?>.*?</ref>      | # exclude <ref> notes
        ^[\ \t]*({\||[|!]).*?$ | # exclude wikitable
        </*nowiki>             | # remove <nowiki> tags
        {{.*?}}                | # remove (not nested) template
        <math>.*?</math>       | # remove LaTeX staff
        [\[\]]                 | # remove [, ]
        ^[*:;]+                | # remove *, :, ; in begin of line
        <!--                   |
        -->                    |
    )
    """ % flags, "", text)

    if remove_quote:
        # '' text ''
        # '' text ''.
        # '' text '' (text)
        # « text »
        # ...
        #

        italic_quoteC = re.compile("(?m)^[:*]?\s*(''.*?'')\.?\s*(\(.*?\))?\r?$")
        italic_quoteC = re.compile("(?m)^[:*]?\s*('''.*?''')\.?\s*(\(.*?\))?\r?$")

        index = 0
        try:
            import pywikiparser
        except ImportError:
            pywikiparser = False

        while pywikiparser:
            m = italic_quoteC.search(text, index)
            if not m:
                break

            s = pywikiparser.Parser(m.group(1))

            try:
                xmldata = s.parse().toxml()
                if '<wikipage><p><i>' in xmldata and '</i></p></wikipage>' in xmldata:
                    if xmldata.count('<i>') == 1:
                        text = text[:m.start()] + text[m.end():]
            except:
                pass

            index = m.start() + 1

        text = re.sub('(?m)^[:*]*\s*["][^"]+["]\.?\s*(\(.*?\))?\r?$', "", text)
        text = re.sub('(?m)^[:*]*\s*[«][^»]+[»]\.?\s*(\(.*?\))?\r?$', "", text)
        text = re.sub('(?m)^[:*]*\s*[“][^”]+[”]\.?\s*(\(.*?\))?\r?$', "", text)

    # remove useless spaces
    text = re.sub("(?m)(^[ \t]+|[ \t]+\r?$)", "", text)

    if debug:
        write_log(text+'\n', "copyright/wikicode_removed.txt")

    return text

def skip_section(text):
    sect_titles = '|'.join(sections_to_skip[pywikibot.getSite().lang])
    sectC = re.compile('(?mi)^==\s*(' + sect_titles + ')\s*==')
    while True:
        newtext = cut_section(text, sectC)
        if newtext == text:
            break
        text = newtext
    return text

def cut_section(text, sectC):
    sectendC = re.compile('(?m)^==[^=]')
    start = sectC.search(text)
    if start:
        end = sectendC.search(text, start.end())
        if end:
            return text[:start.start()]+text[end.start():]
        else:
            return text[:start.start()]
    return text
# end predefine

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
            content = page.get()
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

        content = skip_section(content)
        content = remove_wikicode(content)
        clist = content.splitlines()
        content = u""
        for i in clist: content += i
        
        pywikibot.output(u"check " + page.title())
        
        if checkVandal(content):
            with open(os.path.join(env['WORKPATH'], 'havechecked.txt'), "r") as f:
                lines = f.readlines()
            
            if page.title() in lines: continue
            
            pywikibot.output(page.title() + u" is vandal!!")
            
            with open(os.path.join(env['WORKPATH'], 'havechecked.txt'), "a") as f:
                f.write(page.title().encode("utf8"))
            
            page.put(u"{{ลบ|บอตแจ้งก่อกวนหรือไม่เป็นสารานุกรม}}", 
            u"บอตแจ้งก่อกวนหรือไม่เป็นสารานุกรม หากผิดพลาด โปรดแจ้ง[[คุยกับผู้ใช้:Nullzero|ที่นี่]]")
