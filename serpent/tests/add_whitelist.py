#!/usr/bin/python2
import re
import os
from colorama import init, Style, Fore

init()

extern = '''
extern whitelist: [addAddress:ii:s, check:i:i, checkaddr:ii:i, replaceAddress:iii:s]
data whitelist
'''

PARENTDIR = os.path.split(os.getcwd())[:-1][0]

FUNCTION_PATHS = os.walk(os.path.join(PARENTDIR, 'function files')).next()
API_PATHS = os.walk(os.path.join(PARENTDIR, 'data and api files')).next()

filedata = {}

for paths in (FUNCTION_PATHS, API_PATHS):
    pathdir, _, names = paths
    for name in names:
        filepath = os.path.join(pathdir, name)
        write = False
        with open(filepath) as f:
            filedata[name] = f.read()
            if extern not in filedata[name]:
                print Style.BRIGHT + Fore.YELLOW + 'adding whitelist externs to', Style.BRIGHT + Fore.RED + name, Style.RESET_ALL
                write = True
                if 'def init():' in filedata[name]:
                    lines = filedata[name].split('\n')
                    for i, line in enumerate(lines):
                        if line.startswith('def init():'):
                            lines[i] = line + '\n    self.whitelist = 0xf1e4b1b0d357ded7a34c08dcac1a5d8d1eda795c\n'
                            break
                    filedata[name] = extern + '\n'.join(lines)
                else:
                    definit = 'def init():\n    self.whitelist = 0xf1e4b1b0d357ded7a34c08dcac1a5d8d1eda795c\n'
                    filedata[name] = extern + definit + filedata[name]
        if write:
            with open(filepath, 'w') as f:
                f.write(filedata[name])
