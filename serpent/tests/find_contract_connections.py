import os
import re
from collections import defaultdict
from colorama import Style, Fore, init

init()

MY_PATH = os.path.split(os.getcwd())[:-1][0]
#print MY_PATH

PATH1 = os.walk(os.path.join(MY_PATH, 'function files')).next()
PATH2 = os.walk(os.path.join(MY_PATH, 'data and api files')).next()

#print PATH1, PATH2

data = {}
data2 = defaultdict(list)
for name in PATH2[-1]:
#    print 'searching for', name, 'requirements'
    createp = re.compile("(?P<name>[A-Z]+) = create\('{}'\)".format(name))
    for oname in PATH1[-1]:
        if oname not in data:
#            print 'reading', oname
            data[oname] = open(os.path.join(PATH1[0], oname)).read()
        if createp.search(data[oname]):
            data2[oname].append(name)

for i, name in enumerate(PATH2[-1][:-1]):
#    print 'searching for', name, 'requirements'
    createp = re.compile("(?P<name>[A-Z]+) = create\('{}'\)".format(name))
    for oname in PATH2[-1][i+1:]:
        if oname not in data:
#            print 'reading', oname
            data[oname] = open(os.path.join(PATH2[0], oname)).read()
        if createp.search(data[oname]):
            data2[oname].append(name)

name_Style = Style.BRIGHT + Fore.YELLOW
deps_Style = Style.BRIGHT + Fore.RED

for k, v in sorted(list(data2.items())):
    print name_Style + k, Style.RESET_ALL + 'depends on', ', '.join(deps_Style + d + Style.RESET_ALL for d in sorted(v)[:-1])+', and '+deps_Style + sorted(v)[-1]
    print Style.RESET_ALL
