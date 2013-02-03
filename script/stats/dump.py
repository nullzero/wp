# -*- coding: utf-8 -*-

import datetime, urllib, re, os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try: from lib import preload
except:
    print "เรียกใช้ไลบรารีไม่ได้ จบการทำงาน!"
    sys.exit()

import wikipedia as pywikibot

site = preload.site

def dlProgress(count, blockSize, totalSize):
    percent = int(count * blockSize * 100 / totalSize)
    sys.stdout.write("\r...%d%%" % percent)
    sys.stdout.flush()

year = datetime.date.today().year
month = datetime.date.today().month
url = "http://dumps.wikimedia.org/other/pagecounts-raw/%s/%s-%02d" % (year, year, int(month))
f = urllib.urlopen(url)
content = f.read()
filename = re.findall("pagecounts.*?\.gz", content)[-1]
urllib.urlretrieve(os.path.join(url, filename), "DLFILE.gz", reporthook=dlProgress)
os.system("gunzip --force DLFILE.gz")
filename = filename[:-len(".gz")]
cbreak = False
lines = []
page = pywikibot.Page(site, u"ผู้ใช้:Nullzerobot/stats")

with open(filename, "r") as f:
    for line in f:
        if line.startswith("th"):
            cbreak = True
            lines.append(line.split(' '))
        elif cbreak:
            break

lines = sorted(lines, key=lambda x: int(x[2]), reverse = True)
content = u""
content = []
ptr = -1
while len(content) <= 100:
    ptr += 1
    name = eval('"%s"' % urllib.unquote(urllib.unquote(lines[ptr][1])))
    if ":" in name: continue
    if re.search("^undefined$", name, flags = re.IGNORECASE) is not None: continue
    if name == u"th": continue
    content.append(u"| %s || %s\n|-\n" % (name.decode("utf-8").replace(u"_", u" "), lines[ptr][2].decode("utf-8")))
content = u'{| class = "wikitable"\n|-\n! บทความ !! จำนวนยอดผู้เข้าชม\n' + u"".join(content) + u'|}'
print content
page.put(content, u"ปรับปรุงรายการ")
pywikibot.stopme()
