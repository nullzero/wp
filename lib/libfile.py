# -*- coding: utf-8  -*-

import sys, os, re

try: import preload
except:
    print "เรียกใช้ไลบรารีไม่ได้ จบการทำงาน!"
    sys.exit()

base = os.path.abspath(os.path.dirname(sys.argv[0]))

def deUnicode(value):
    try: value = str(value)
    except UnicodeEncodeError: value = value.encode("utf-8")
    return value

def get(filename, key):
    key = deUnicode(key)
    filename = deUnicode(filename)
    
    fullfilename = os.path.join(base, filename + ".dat")
    with open(fullfilename, "r") as f: s = f.read()
    return re.search("(?m)^" + re.escape(key) + ": (.*?)$", s).group(1)

def put(filename, key, value):
    key = deUnicode(key)
    value = deUnicode(value)
    filename = deUnicode(filename)
    fullfilename = os.path.join(base, filename + ".dat")
    
    s = u""
    try:
        with open(fullfilename, "r") as f: s = f.read()
    except: pass
        
    try:
        get(filename, key)
        s = re.sub("(?m)^%s: (.*?)$" % re.escape(key), "%s: %s" % (re.escape(key), value), s)
    except:
        if s.strip(): s = s.strip() + "\n" + key + ": " + value
        else: s = key + ": " + value
        
    with open(fullfilename, "w") as f: f.write(s)
