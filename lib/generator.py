# -*- coding: utf-8  -*-

try: import preload
except:
    print "Cannot import preload. Exit!"
    sys.exit()

import pagegenerators

def CatGenerator(catname):
    return pagegenerators.GeneratorFactory().getCategoryGen(catname, 0)
