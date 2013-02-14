#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try: from lib import preload
except:
    print(traceback.format_exc().decode("utf-8"))
    print "เรียกใช้ไลบรารีไม่ได้ จบการทำงาน!"
    sys.exit()
    
from wikipedia import *

