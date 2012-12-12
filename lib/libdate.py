# -*- coding: utf-8  -*-

import datetime

try: import preload
except:
    print "Cannot import preload. Exit!"
    sys.exit()

def getTime(): return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def wrapMonth(m):
    m -= 1
    if m < 0: m += 12
    if m >= 12: m -= 12
    return m

def monthThai(m):
    return [u"มกราคม", u"กุมภาพันธ์", u"มีนาคม", u"เมษายน", u"พฤษภาคม", u"มิถุนายน", 
            u"กรกฎาคม", u"สิงหาคม", u"กันยายน", u"ตุลาคม", u"พฤศจิกายน", u"ธันวาคม"][wrapMonth(m)]
            
def monthThaiAbbr(m):
    return [u"ม.ค.", u"ก.พ.", u"มี.ค.", u"เม.ย.", u"พ.ค.", u"มิ.ย.", 
            u"ก.ค.", u"ส.ค.", u"ก.ย.", u"ต.ค.", u"พ.ย.", u"ธ.ค."][wrapMonth(m)]


class date(datetime.date):
    pass
