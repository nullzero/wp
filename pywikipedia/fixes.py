# -*- coding: utf-8 -*-

__version__ = '$Id: fixes.py 10667 2012-11-07 08:59:44Z xqt $'

help = u'''
                  * HTML        - Convert HTML tags to wiki syntax, and
                                  fix XHTML.
                                    **) NOTE below
                  * isbn        - Fix badly formatted ISBNs.
                                    **) NOTE below
                  * syntax      - Try to fix bad wiki markup. Do not run
                                  this in automatic mode, as the bot may
                                  make mistakes.
                  * syntax-safe - Like syntax, but less risky, so you can
                                  run this in automatic mode.
                                    **) NOTE below
                  * case-de     - fix upper/lower case errors in German
                  * grammar-de  - fix grammar and typography in German
                  * vonbis      - Ersetze Binde-/Gedankenstrich durch 'bis'
                                  in German
                  * music       - Links auf Begriffsklärungen in German
                  * datum       - specific date formats in German
                  * correct-ar  - Corrections for Arabic Wikipedia and any
                                  Arabic wiki.
                  * yu-tld      - the yu top-level domain will soon be
                                  disabled, see
                  * fckeditor   - Try to convert FCKeditor HTML tags to wiki
                                  syntax.
                                  http://lists.wikimedia.org/pipermail/wikibots-l/2009-February/000290.html

                                    **) NOTE: these fixes are part of the
                                        cosmetic_changes.py. You may use
                                        that script instead.

'''

fixes = {
    # These replacements will convert HTML to wiki syntax where possible, and
    # make remaining tags XHTML compliant.
    'HTML': {
        'regex': True,
        'msg': {
            'th':u'โรบอต: แก้ HTML มาเป็นรูปแบบวิกิ',
        },
        'replacements': [
            # Everything case-insensitive (?i)
            # Keep in mind that MediaWiki automatically converts <br> to <br />
            # when rendering pages, so you might comment the next two lines out
            # to save some time/edits.
            #(r'(?i)<br>',                      r'<br />'),
            # linebreak with attributes
            #(r'(?i)<br ([^>/]+?)>',            r'<br \1 />'),
            (r'(?i)<b>(.*?)</b>',              r"'''\1'''"),
            (r'(?i)<strong>(.*?)</strong>',    r"'''\1'''"),
            (r'(?i)<i>(.*?)</i>',              r"''\1''"),
            (r'(?i)<em>(.*?)</em>',            r"''\1''"),
            # horizontal line without attributes in a single line
            (r'(?i)([\r\n])<hr[ /]*>([\r\n])', r'\1----\2'),
            # horizontal line without attributes with more text in the same line
            #(r'(?i) +<hr[ /]*> +',             r'\r\n----\r\n'),
            # horizontal line with attributes; can't be done with wiki syntax
            # so we only make it XHTML compliant
            (r'(?i)<hr ([^>/]+?)>',            r'<hr \1 />'),
            # a header where only spaces are in the same line
            (r'(?i)([\r\n]) *<h1> *([^<]+?) *</h1> *([\r\n])',  r'\1= \2 =\3'),
            (r'(?i)([\r\n]) *<h2> *([^<]+?) *</h2> *([\r\n])',  r'\1== \2 ==\3'),
            (r'(?i)([\r\n]) *<h3> *([^<]+?) *</h3> *([\r\n])',  r'\1=== \2 ===\3'),
            (r'(?i)([\r\n]) *<h4> *([^<]+?) *</h4> *([\r\n])',  r'\1==== \2 ====\3'),
            (r'(?i)([\r\n]) *<h5> *([^<]+?) *</h5> *([\r\n])',  r'\1===== \2 =====\3'),
            (r'(?i)([\r\n]) *<h6> *([^<]+?) *</h6> *([\r\n])',  r'\1====== \2 ======\3'),
            # TODO: maybe we can make the bot replace <p> tags with \r\n's.
        ],
        'exceptions': {
            'inside-tags': [
                'nowiki',
                'comment',
                'math',
                'pre'
            ],
        }
    },

    # Do NOT run this automatically!
    # Recommendation: First run syntax-safe automatically, afterwards
    # run syntax manually, carefully checking that you're not breaking
    # anything.
    'syntax': {
        'regex': True,
        'msg': {
            'th':u'โรบอต: แก้ syntax ของวิกิพีเดีย',
        },
        'replacements': [
            # external link in double brackets
            (r'\[\[(?P<url>https?://[^\]]+?)\]\]',   r'[\g<url>]'),
            # external link starting with double bracket
            (r'\[\[(?P<url>https?://.+?)\]',   r'[\g<url>]'),
            # external link with forgotten closing bracket
            #(r'\[(?P<url>https?://[^\]\s]+)\r\n',  r'[\g<url>]\r\n'),
            # external link ending with double bracket.
            # do not change weblinks that contain wiki links inside
            # inside the description
            (r'\[(?P<url>https?://[^\[\]]+?)\]\](?!\])',   r'[\g<url>]'),
            # external link and description separated by a dash.
            # ATTENTION: while this is a mistake in most cases, there are some
            # valid URLs that contain dashes!
            (r'\[(?P<url>https?://[^\|\]\s]+?) *\| *(?P<label>[^\|\]]+?)\]', r'[\g<url> \g<label>]'),
            # wiki link closed by single bracket.
            # ATTENTION: There are some false positives, for example
            # Brainfuck code examples or MS-DOS parameter instructions.
            # There are also sometimes better ways to fix it than
            # just putting an additional ] after the link.
            (r'\[\[([^\[\]]+?)\](?!\])',  r'[[\1]]'),
            # wiki link opened by single bracket.
            # ATTENTION: same as above.
            (r'(?<!\[)\[([^\[\]]+?)\]\](?!\])',  r'[[\1]]'),
            # template closed by single bracket
            # ATTENTION: There are some false positives, especially in
            # mathematical context or program code.
            (r'{{([^{}]+?)}(?!})',       r'{{\1}}'),
        ],
        'exceptions': {
            'inside-tags': [
                'nowiki',
                'comment',
                'math',
                'pre',
                'source',        # because of code examples
                'startspace',    # because of code examples
            ],
            'text-contains': [
                r'http://.*?object=tx\|',               # regular dash in URL
                r'http://.*?allmusic\.com',             # regular dash in URL
                r'http://.*?allmovie\.com',             # regular dash in URL
                r'http://physics.nist.gov/',            # regular dash in URL
                r'http://www.forum-seniorenarbeit.de/', # regular dash in URL
                r'http://kuenstlerdatenbank.ifa.de/',   # regular dash in URL
                r'&object=med',                         # regular dash in URL
                r'\[CDATA\['                            # lots of brackets
            ],
        }
    },

    # The same as syntax, but restricted to replacements that should
    # be safe to run automatically.
    'syntax-safe': {
        'regex': True,
        'msg': {
            'th':u'โรบอต: แก้ syntax ของวิกิพีเดีย',
        },
        'replacements': [
            # external link in double brackets
            (r'\[\[(?P<url>https?://[^\]]+?)\]\]',   r'[\g<url>]'),
            # external link starting with double bracket
            (r'\[\[(?P<url>https?://.+?)\]',   r'[\g<url>]'),
            # external link with forgotten closing bracket
            #(r'\[(?P<url>https?://[^\]\s]+)\r\n',   r'[\g<url>]\r\n'),
            # external link and description separated by a dash, with
            # whitespace in front of the dash, so that it is clear that
            # the dash is not a legitimate part of the URL.
            (r'\[(?P<url>https?://[^\|\] \r\n]+?) +\| *(?P<label>[^\|\]]+?)\]', r'[\g<url> \g<label>]'),
            # dash in external link, where the correct end of the URL can
            # be detected from the file extension. It is very unlikely that
            # this will cause mistakes.
            (r'\[(?P<url>https?://[^\|\] ]+?(\.pdf|\.html|\.htm|\.php|\.asp|\.aspx|\.jsp)) *\| *(?P<label>[^\|\]]+?)\]', r'[\g<url> \g<label>]'),
        ],
        'exceptions': {
            'inside-tags': [
                'nowiki',
                'comment',
                'math',
                'pre',
                'source',        # because of code examples
                'startspace',    # because of code examples
            ],
        }
    },
    
    'nullzero': {
        'regex': True,
        'msg'  : {
            'th:': u'โรบอต: แก้คำผิด',
        },
        'replacements' : [
            (u'กฏ',  u'กฎ'),
            (u'เกมส์', u'เกม'),
            (u'(ก๊กกะ|กิ๊กกะ|กิกะ)', u'จิกะ'),
            (u'กรกฏาคม', u'กรกฎาคม'),
            (u'กระทั้ง', u'กระทั่ง'),
            (u'กงศุล',  u'กงสุล'),
            (u'กบฎ',  u'กบฏ'),
            (u'ปาฏิหารย์',  u'ปาฏิหาริย์'),
            (u'สังเกตุ',  u'สังเกต'),
            (u'อนุญาติ',  u'อนุญาต'),
            (u'ซอฟ(ท์?|ต)?แวร์',  u'ซอฟต์แวร์'),
            (u'(เบราว?เซอร์|บราว์?เซอร์)',  u'เบราว์เซอร์'),
            (u'ไมโครซอฟต์',  u'ไมโครซอฟท์'),
            (u'อินเ[ทต]อ(ร์?)?เน็?[ตท]',  u'อินเทอร์เน็ต'),
            (u'อีเมล์',  u'อีเมล'),
            (u'กราฟฟิ[คก]', u'กราฟิก'),
            (u'กษัตรย์', u'กษัตริย์'),
            (u'กิติมศักดิ์', u'กิตติมศักดิ์'),
            (u'ขาดดุลย์', u'ขาดดุล'),
            (u'คริสตศตวรรษ', u'คริสต์ศตวรรษ'),
            (u'คริสตศักราช', u'คริสต์ศักราช'),
            (u'คริสตศาสนา', u'คริสต์ศาสนา'),
            (u'คริสต์กาล', u'คริสตกาล'),
            (u'คริสต์เตียน', u'คริสเตียน'),
            (u'คริสมาส(ต์)?', u'คริสต์มาส'),
            (u'คลีนิก', u'คลินิก'),
            (u'คำนวน', u'คำนวณ'),
            (u'เคเบิ้ล', u'เคเบิล'),
            (u'จักรสาน', u'จักสาน'),
            (u'โครงการณ์', u'โครงการ'),
            (u'งบดุลย์', u'งบดุล'),
            (u'ซีรี่ส์', u'ซีรีส์'),
            (u'ซีรีย์', u'ซีรีส์'),
            (u'ซีรี่ย์', u'ซีรีส์'),
            (u'เซ็นติ', u'เซนติ'),
            (u'เซอร์เวอร์', u'เซิร์ฟเวอร์'),
            (u'ฑูต', u'ทูต'),
            (u'ดอทคอม', u'ดอตคอม'),
            (u'ด็อทคอม', u'ดอตคอม'),
            (u'ด็อตคอม', u'ดอตคอม'),
            (u'ดอทเน็ท', u'ดอตเน็ต'),
            (u'ดอตเน็ท', u'ดอตเน็ต'),
            (u'ด็อตเน็ต', u'ดอตเน็ต'),
            (u'ด็อทเน็ต', u'ดอตเน็ต'),
            (u'ดอทเน็ต', u'ดอตเน็ต'),
            (u'ดอทเนท', u'ดอตเน็ต'),
            (u'ถ่วงดุลย์', u'ถ่วงดุล'),
            (u'ทะเลสาป', u'ทะเลสาบ'),
            (u'เทมเพลท', u'เทมเพลต'),
            (u'ธุระกิจ', u'ธุรกิจ'),
            (u'นิวยอร์ค', u'นิวยอร์ก'),
            (u'บรรได', u'บันได'),
            (u'บรรเทิง', u'บันเทิง'),
            (u'บล็อค', u'บล็อก'),
            (u'บล๊อค', u'บล็อก'),
            (u'บล๊อก', u'บล็อก'),
            (u'เบรค', u'เบรก'),
            (u'ไบท์', u'ไบต์'),
            (u'ปฎิ', u'ปฏิ'),
            (u'ปฏิกริยา', u'ปฏิกิริยา'),
            (u'ปฎิกริยา', u'ปฏิกิริยา'),
            (u'ปรากฎ', u'ปรากฏ'),
            (u'ปราถนา', u'ปรารถนา'),
            (u'ปีรามิด', u'ปิระมิด', u'พีระมิด'),
            (u'โปรเจค', u'โปรเจกต์'),
            (u'โปรเจคท์', u'โปรเจกต์'),
            (u'โปรเจคต์', u'โปรเจกต์'),
            (u'โปรเจ็ค', u'โปรเจกต์'),
            (u'โปรเจ็คท์', u'โปรเจกต์'),
            (u'โปรเจ็คต์', u'โปรเจกต์'),
            (u'โปรโตคอล', u'โพรโทคอล'),
            (u'ผลลัพท์', u'ผลลัพธ์'),
            (u'ผูกพันธ์', u'ผูกพัน'),
            (u'ฝรั่งเศษ', u'ฝรั่งเศส'),
            (u'ฟังก์ชั่น', u'ฟังก์ชัน'),
            (u'ภาพยนต์', u'ภาพยนตร์'),
            (u'มิวสิค', u'มิวสิก'),
            (u'เยอรมันนี', u'เยอรมนี'),
            (u'รถยนตร์', u'รถยนต์'),
            (u'ล็อค', u'ล็อก'),
            (u'ลอส แองเจลิส', u'ลอสแอนเจลิส'),
            (u'ลอส แองเจลลิส', u'ลอสแอนเจลิส'),
            (u'ลอส แองเจลีส', u'ลอสแอนเจลิส'),
            (u'ลอสแองเจลิส', u'ลอสแอนเจลิส'),
            (u'ลอสแองเจลีส', u'ลอสแอนเจลิส'),
            (u'ลอสแองเจลลิส', u'ลอสแอนเจลิส'),
            (u'ลอสแองเจอลิส', u'ลอสแอนเจลิส'),
            (u'ลอสแองเจอลีส', u'ลอสแอนเจลิส'),
            (u'ลอสแอนเจลลิส', u'ลอสแอนเจลิส'),
            (u'ลายเซ็นต์', u'ลายเซ็น'),
            (u'ลิ้งค์', u'ลิงก์'),
            (u'ลิ๊งค์', u'ลิงก์'),
            (u'ลิ้งก์', u'ลิงก์'),
            (u'ลิ๊งก์', u'ลิงก์'),
            (u'เวคเตอร์', u'เวกเตอร์'),
            (u'เวทย์มนตร์', u'เวทมนตร์'),
            (u'เวทย์มนต์', u'เวทมนตร์'),
            (u'เวทมนต์', u'เวทมนตร์'),
            (u'เวบไซท์', u'เว็บไซต์'),
            (u'เวบไซต์', u'เว็บไซต์'),
            (u'เวบไซท์', u'เว็บไซต์'),
            (u'เว็บไซท์', u'เว็บไซต์'),
            (u'เว็บไซต์์', u'เว็บไซต์'),
            (u'เวอร์ชั่น', u'เวอร์ชัน'),
            (u'เวิล์ด', u'เวิลด์'),
            (u'ศรีษะ', u'ศีรษะ'),
            (u'สคริปท์', u'สคริปต์'),
            (u'สครปต์', u'สคริปต์'),
            (u'สเตชั่น', u'สเตชัน'),
            (u'สมดุลย์', u'สมดุล'),
            (u'สวดมน', u'สวดมนต์'),
            (u'สวดมนตร์', u'สวดมนต์'),
            (u'สวรรณคต', u'สวรรคต'),
            (u'อโดบี', u'อะโดบี'),
            (u'อานิเมะ', u'อะนิเมะ'),
            (u'อลูมิเนียม', u'อะลูมิเนียม'),
            (u'ออบเจ็ค', u'อ็อบเจกต์'),
            (u'ออปเจ็ค', u'อ็อบเจกต์'),
            (u'ออปเจค', u'อ็อบเจกต์'),
            (u'อัพเด็ต', u'อัปเดต'),
            (u'อัพเดต', u'อัปเดต'),
            (u'อัพเดท', u'อัปเดต'),
            (u'อัปเด็ต', u'อัปเดต'),
            (u'อัพโหลด', u'อัปโหลด'),
            (u'อิเล็กโทรนิกส์', u'อิเล็กทรอนิกส์'),
            (u'อิสระภาพ', u'อิสรภาพ'),
            (u'เอ็นจิ้น', u'เอนจิน'),
            (u'เอ็นจิน', u'เอนจิน'),
            (u'เอนจิ้น', u'เอนจิน'),
            (u'เอล์ฟ', u'เอลฟ์'),
            (u'เอาท์พุต', u'เอาต์พุต'),
            (u'เอาท์พุท', u'เอาต์พุต'),
            (u'แอปพลิเคชั่น', u'แอปพลิเคชัน'),
            (u'แอพพลิเคชั่น', u'แอปพลิเคชัน'),
            (u'แอพพลิเคชัน', u'แอปพลิเคชัน'),
            (u'แอพพลิคเคชัน', u'แอปพลิเคชัน'),
            (u'<references\s+/>', u'{{รายการอ้างอิง}}'),
        ],
    },
}

import config

try:
    execfile(config.datafilepath(config.base_dir, 'user-fixes.py'))
except IOError:
    pass
