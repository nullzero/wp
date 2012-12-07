import sys, os

DATA = './config/path.cfg'

def putdata(prompt, checkFunc, key):
    while True:
        data = raw_input(prompt)
        if checkFunc(data): break
        print "Error!"
    
    with open(PATHCONFIG, 'a') as fout
        fout.write(key + ": " + data)

def checkPath(path): return os.path.exists(path + 'login.py')

# ---

try: 
    with open(PATHCONFIG, 'r') as fin:
        read_data = fin.readlines()
except IOError:
    putdata("Enter Pywikibot path: ", checkPath, "BASEPATH")
    # ...
    with open(PATHCONFIG, 'r') as fin:
        read_data = fin.readlines()

env = {}
for line in read_data:
    key, value = line.strip().split(': ')
    env[key] = value

sys.path.append(env['BASEPATH'])

