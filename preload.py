# -*- coding: utf-8  -*-

import codecs, os, re, sys, datetime

DATACONFIG = os.path.join(os.path.abspath(os.path.dirname(__file__)), "config/data.cfg")

console_encoding = sys.stdout.encoding

if console_encoding is None or sys.platform == 'cygwin':
    console_encoding = "iso-8859-1"

def getTime(): return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
    with open(DATACONFIG, 'r') as fin: read_data = fin.readlines()
    env = {}
    for line in read_data:
        key, value = line.strip().split(': ')
        
        if key == 'SYSOP': value = (value == 'y')
        if key == 'BASEPATH': value = simplifypath(value)
        
        env[key] = value
    return env
    
def putdata(key, prompt = None, checkFunc = lambda func: True, data = None, parser = lambda dat: dat):
    if prompt is not None:
        while True:
            data = raw_input(prompt)
            if checkFunc(data): break
            print "Error!"
    
    with open(DATACONFIG, 'a') as fout:
        fout.write(key + ": " + parser(data) + "\n")

def simplifypath(path):
    return os.path.abspath(os.path.expanduser(path))

# ---

try: open(DATACONFIG, 'r').close()
except IOError:
    # BASEPATH
    putdata("BASEPATH",
        "Enter Pywikibot path: ", 
        lambda path: os.path.exists(simplifypath(os.path.join(path, "login.py"))),
        parser = lambda path: simplifypath(path))
    # USERNAME
    putdata("USER", "Enter username: ")
    # PASSWORD
    putdata("PASS", "Enter password: ")
    # SYSOP
    putdata("SYSOP", "Are you a sysop (y/n): ", lambda ans: ans in "yn")
    # TMP
    putdata("TMP", data = "/tmp")
    # WORKPATH
    putdata("WORKPATH", data = simplifypath(os.path.dirname(__file__)))
    # ...

env = loadConfig()
sys.path.append(env['BASEPATH'])

if not os.path.exists(os.path.join(env['BASEPATH'], "user-config.py")):
    create_user_config(env['BASEPATH'], env['USER'])
    env = loadConfig()

import wikipedia as pywikibot

site = pywikibot.getSite()
if not site.loggedInAs(sysop = env['SYSOP']):
    pywikibot.output("I have not logged in yet!")
    import shlex, subprocess
    args = shlex.split("python " + os.path.join(env['BASEPATH'], "login.py") + " -pass:" + env['PASS'])
    process = subprocess.call(args)
    pywikibot.output("Just logged in.")
