import os
import sys
if not os.isatty(sys.stdout.fileno()):
    with open("/home/sorawee/Desktop/file.txt", "w") as fin:
        fin.write("oak")
