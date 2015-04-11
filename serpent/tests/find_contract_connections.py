#!/usr/bin/python2
import os
import re
from collections import defaultdict
from colorama import Style, Fore, init
import serpent

init()

PARENTDIR = os.path.split(os.getcwd())[:-1][0]

FUNCTION_PATHS = os.walk(os.path.join(PARENTDIR, 'function files')).next()
API_PATHS = os.walk(os.path.join(PARENTDIR, 'data and api files')).next()

filedata = {}
dependcounts = defaultdict(int)
for paths in (FUNCTION_PATHS, API_PATHS):
    pathdir, _, names = paths
    for name in names:
        createp = re.compile("[A-Z]+ = create\('{}'\)".format(name))
        for opaths in (FUNCTION_PATHS, API_PATHS):
            opathdir, _, onames = opaths
            for oname in onames:
                if oname == name:
                    continue
                if oname not in filedata:
                    filedata[oname] = open(os.path.join(opathdir, oname)).read()
                if createp.search(filedata[oname]):
                    dependcounts[name] += 1

for k, v in sorted(dependcounts.items()):
    if v:
        print k, 'has', v, 'dependencies'
