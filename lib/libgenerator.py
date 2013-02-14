# -*- coding: utf-8  -*-

import sys

try: import preload
except:
    print "เรียกใช้ไลบรารีไม่ได้ จบการทำงาน!"
    sys.exit()

import pagegenerators

def CatGenerator(catname):
    return pagegenerators.GeneratorFactory().getCategoryGen(u':' + catname, 0)
