#!/usr/bin/python
import sys
from pyrpctools import DB
import json
import os

SRCPATH = 'src'

def error(msg):
    print ERROR, msg
    print 'ABORTING'
    sys.exit(1)

def get_fullname(name):
    '''
    Takes a short name from an import statement and
    returns a real path to that contract.
    '''
    for directory, subdirs, files in os.walk(SRCPATH):
        for f in files:
            if f[:-3] == name:
                return os.path.join(directory, f)
    error('No contract with that name: '+name)

def main():
    for line in open(get_fullname(sys.argv[1])):
        line = line.rstrip()
        if line.startswith('import'):
            line = line.split(' ')
            name, sub = line[1], line[3]
            info = json.loads(DB.Get(name))
            print info['sig']
            print sub, '=', info['address']
            print
    sys.exit(0)

if __name__ == '__main__':
    main()
