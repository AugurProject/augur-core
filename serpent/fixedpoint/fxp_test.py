#!/usr/bin/python2
import cStringIO
import sys
### Get rid of the nasty junk printed
### when pyethereum is imported
STDOUT = sys.stdout
FAKE_STDOUT = cStringIO.StringIO() 
sys.stdout = FAKE_STDOUT
from pyethereum import tester as t
sys.stdout = STDOUT
#####################################
import gmpy2
import random

gmpy2.get_context().precision = 256

def printf(stuff, *args):
    sys.stdout.write(stuff % args)
    sys.stdout.flush()

def main():
    s = t.state()
    printf('Compiling...\t')
    c = s.abi_contract('fixedpoint.se')
    printf('Done.\n')
    s.mine(1)

    for f in c:
        for i in range(30):
            
