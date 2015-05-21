import subprocess
import sys
import os

MASTER = '../augur-core/serpent/'
CODE = 'data and api files', 'function files', 'consensus', 

if __name__ == '__main__':
    for path in CODE:
        subprocess.call(['cp', '-R', MASTER+path, 'src/'])
