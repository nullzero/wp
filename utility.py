import sys, os

DATACONFIG = os.path.dirname(sys.argv[0]) + '/config/data.cfg'

def putdata(prompt, checkFunc, key):
    while True:
        data = raw_input(prompt)
        if checkFunc(data): break
        print "Error!"
    
    with open(DATACONFIG, 'a') as fout:
        fout.write(key + ": " + data + "\n")

# ---

try: 
    with open(DATACONFIG, 'r') as fin:
        read_data = fin.readlines()
except IOError:
    # BASEPATH
    putdata("Enter Pywikibot path: ", 
        lambda path: os.path.exists(path + 'login.py'), 
        "BASEPATH")
    # USERNAME
    putdata("Enter username: ", 
        lambda user: True, 
        "USER")
    # PASSWORD
    putdata("Enter password: ", 
        lambda passwd: True, 
        "PASS")
    # ...
    with open(DATACONFIG, 'r') as fin:
        read_data = fin.readlines()

env = {}
for line in read_data:
    key, value = line.strip().split(': ')
    env[key] = value

sys.path.append(env['BASEPATH'])
