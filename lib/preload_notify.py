# -*- coding: utf-8  -*-

import codecs, os, re, sys, datetime, traceback

dataConfigPath = os.path.abspath(os.path.join(os.path.dirname(__file__), "../config/data_notify.cfg"))

console_encoding = sys.stdout.encoding

if console_encoding is None or sys.platform == 'cygwin':
    console_encoding = "iso-8859-1"

def listchoice(clist = [], message = None, default = None):
    if not message: message = "Select"
    if default: message += " (default: %s)" % default
    message += ": "
    for n, i in enumerate(clist): print ("%d: %s" % (n + 1, i))
    
    while True:
        choice = raw_input(message)
        if choice == '' and default: return default
        try: return clist[int(choice) - 1]
        except: print("Invalid response")
        
    return response

def create_user_config(base_dir, username):
    _fnc = os.path.join(base_dir, "user-config.py")
    known_families = re.findall(r'(.+)_family.py\b',
        '\n'.join(os.listdir(os.path.join(base_dir,"families"))))
    fam = listchoice(known_families,
                     "Select family of sites we are working on",
                     default = 'wikipedia')
    mylang = raw_input(
        "The language code of the site we're working on (default: 'en'): ") or 'en'
    username = unicode(username, console_encoding)
    
    while True:
        choice = raw_input(
    "Which variant of user_config.py:\n[S]mall or [E]xtended (with further information)? ").upper()
        if choice in "SE": break

    f = codecs.open(os.path.join(base_dir, "config.py"), "r", "utf-8")
    cpy = f.read()
    f.close()

    res = re.findall("^(############## (?:LOGFILE|"
                                        "INTERWIKI|"
                                        "SOLVE_DISAMBIGUATION|"
                                        "IMAGE RELATED|"
                                        "TABLE CONVERSION BOT|"
                                        "WEBLINK CHECKER|"
                                        "DATABASE|"
                                        "SEARCH ENGINE|"
                                        "COPYRIGHT|"
                                        "FURTHER) SETTINGS .*?)^(?=#####|# =====)",
                     cpy, re.MULTILINE | re.DOTALL)
    config_text = '\n'.join(res)

    f = codecs.open(_fnc, "w", "utf-8")
    if choice == 'E':
        f.write("""# -*- coding: utf-8  -*-

# This is an automatically generated file. You can find more configuration
# parameters in 'config.py' file.

# The family of sites we are working on. wikipedia.py will import
# families/xxx_family.py so if you want to change this variable,
# you need to write such a file.
family = '%s'

# The language code of the site we're working on.
mylang = '%s'

# The dictionary usernames should contain a username for each site where you
# have a bot account.
usernames['%s']['%s'] = u'%s'


%s""" % (fam, mylang, fam, mylang, username, config_text))
    else:
        f.write("""# -*- coding: utf-8  -*-
family = '%s'
mylang = '%s'
usernames['%s']['%s'] = u'%s'
""" % (fam, mylang, fam, mylang, username))
    f.close()
    print("'%s' written." % _fnc)

def loadConfig():
    with open(dataConfigPath, 'r') as fin: read_data = fin.readlines()
    env = {}
    for line in read_data:
        key, value = line.strip().split(': ')
        
        if key == 'SYSOP': value = (value == 'y')
        if key == 'BASEPATH': value = simplifyPath(value)
        
        env[key] = value
    return env
    
def putData(key, prompt = None, checkFunc = lambda func: True, data = None, parser = lambda dat: dat):
    if prompt is not None:
        while True:
            data = raw_input(prompt)
            if checkFunc(data): break
            print "Error!"
    
    with open(dataConfigPath, 'a') as fout:
        fout.write(key + ": " + parser(data) + "\n")

def simplifyPath(path):
    return os.path.abspath(os.path.expanduser(path))

def error():
    pywikibot.output(traceback.format_exc().decode("utf-8"))

# ---
try: open(dataConfigPath, 'r').close()
except IOError:
    putData('PYWIKI',
        "โปรดใส่ที่อยู่ของ pywikibot: ", 
        lambda path: os.path.exists(simplifyPath(os.path.join(path, "login.py"))),
        parser = lambda path: simplifyPath(path))
    putData('USER', "โปรดใส่ชื่อผู้ใช้: ")
    putData('PASS', "โปรดใส่รหัสผ่าน: ")
    putData('SYSOP', "คุณเป็นผู้ดูแลระบบหรือเปล่า (y/n): ", lambda ans: ans in "yn")
    putData('TMP', data = "/tmp")
    putData('WORK', data = simplifyPath(os.path.join(os.path.dirname(__file__), "..")))
    putData('SANDBOX', "โปรดใส่ชื่อหน้ากระบะทราย (ทดสอบการกระทำผู้ใช้ใหม่): ")

env = loadConfig()
sys.path.append(env['PYWIKI'])

if not os.path.exists(os.path.join(env['PYWIKI'], "user-config.py")):
    env = loadConfig()

import wikipedia as pywikibot

site = pywikibot.getSite()

if not site.loggedInAs(sysop = env['SYSOP']):
    pywikibot.output("ยังไม่ได้ล็อกอินเลย!")
    import shlex, subprocess
    process = subprocess.call(shlex.split("python " + os.path.join(env['PYWIKI'], "login.py") + \
        " -pass:" + env['PASS']))
    pywikibot.output("ล็อกอินแล้วนะ!")

# ---

summarySuffix = u" หากผิดพลาดโปรดแจ้ง[[คุยกับผู้ใช้:Nullzero|ที่นี่]]"

def File(path, name):
    return os.path.join(os.path.dirname(path), name)
