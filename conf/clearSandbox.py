# -*- coding: utf-8 -*-
"""
This is a user configuration file.
"""

import sys, os, re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try: from lib import preload
except:
    print "E: Can't connect to library!"
    sys.exit()

from lib import miscellaneous

"""
Begin configuration section
"""

pagelist = [u"วิกิพีเดีย:ทดลองเขียน"]
# sandboxPages = miscellaneous.sandboxPages
text = u"""{{ทดลองเขียน}}<!-- กรุณาอย่าแก้ไขบรรทัดนี้ ขอบคุณครับ/ค่ะ -- Please leave this line as they are. Thank you! -->
'''สวัสดีชาวโลก'''
''Hello World!''"""
summary = u"ล้างหน้าอัตโนมัติด้วยบอต"

"""
End configuration section
"""
