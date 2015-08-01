#!/usr/bin/python
import subprocess
import sys
import os

MASTER = '../augur-core/serpent/'
NAMEMAP = {
    'data and api files':'data and api', 
    'function files':'functions',
    'consensus':'consensus',
    }

if __name__ == '__main__':
    for oldname, newname in NAMEMAP.items():
        subprocess.call(['rm', '-rf', 'src/'+newname])
        subprocess.call(['cp', '-R', MASTER + oldname, 'src/' + newname])
