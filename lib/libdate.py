# -*- coding: utf-8  -*-

import datetime, sys

try: import preload
except:
    print "เรียกใช้ไลบรารีไม่ได้ จบการทำงาน!"
    sys.exit()

def getTime(): return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def wrapMonth(m):
    m -= 1
    if m < 0: m += 12
    if m >= 12: m -= 12
    return m

def weekdayThai(d):
    return [u"วันจันทร์", u"วันอังคาร", u"วันพุธ", u"วันพฤหัสบดี", u"วันศุกร์", u"วันเสาร์", u"วันอาทิตย์"][d]

def monthEng(m):
    return [u"January", u"February", u"March", u"April", u"May", u"June", 
    u"July", u"August", u"September", u"October", u"November", u"December"][wrapMonth(m)]

def monthThai(m):
    return [u"มกราคม", u"กุมภาพันธ์", u"มีนาคม", u"เมษายน", u"พฤษภาคม", u"มิถุนายน", 
            u"กรกฎาคม", u"สิงหาคม", u"กันยายน", u"ตุลาคม", u"พฤศจิกายน", u"ธันวาคม"][wrapMonth(m)]
            
def monthThaiAbbr(m):
    return [u"ม.ค.", u"ก.พ.", u"มี.ค.", u"เม.ย.", u"พ.ค.", u"มิ.ย.", 
            u"ก.ค.", u"ส.ค.", u"ก.ย.", u"ต.ค.", u"พ.ย.", u"ธ.ค."][wrapMonth(m)]

def getNumDay(year, month):
    if month == 2:
        if year % 400 == 0: return 29
        elif year % 100 == 0: return 28
        elif year % 4 == 0: return 29
        return 28
        
    return [0, 31, 0, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month]

class date(datetime.date):
    pass
