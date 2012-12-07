import sys, os

DATACONFIG = os.path.dirname(os.path.join(sys.path[0], sys.argv[0])) + '/config/data.cfg'

def putdata(key, prompt, checkFunc = lambda func: True, data = None):
    if prompt is not None:
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
    putdata("BASEPATH",
        "Enter Pywikibot path: ", 
        lambda path: os.path.exists(path + 'login.py'), 
        )
    # USERNAME
    putdata("USER",
        "Enter username: ")
    # PASSWORD
    putdata("PASS",
        "Enter password: ")
    # TMP
    putdata("TMP",
        None,
        "/tmp/")
    # ...
    with open(DATACONFIG, 'r') as fin:
        read_data = fin.readlines()

env = {}
for line in read_data:
    key, value = line.strip().split(': ')
    env[key] = value

sys.path.append(env['BASEPATH'])
