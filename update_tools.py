#!/usr/bin/python
import os
from colorama import Fore, Back, Style, init; init()

def highlighted(s):
    return Style.BRIGHT + Fore.BLACK + Back.YELLOW + s + Style.RESET_ALL

externs = set()
insets = set()

def main():
    for dir_, subdirs, files in os.walk('src'):
        for filename in files:
            if filename.endswith('.se'):
                code = open(os.path.join(dir_, filename))
                for line in code:
                    if line.startswith('extern'):
                        externs.add(code.name)
                    if line.startswith('inset'):
                        insets.add(code.name)

def list_files(func):
    def new_func(*args, **kwds):
        if len(externs) == 0 or len(insets) == 0:
            main()
        result = func(*args, **kwds)
        return result
    new_func.__name__ = func.__name__
    return new_func

@list_files
def print_externs():
    print 'externs:'
    for i in sorted(externs):
        print ' '*4+i

@list_files
def print_insets():
    print 'insets:'
    for i in sorted(insets):
        print ' '*4+i

class Code(object):
    def __init__(self, filename):
        self.filename = filename
        with open(filename) as f:
            self.code = f.read()
        
    def replace(self, s1, s2):
        self.code = self.code.replace(s1, s2)
        
    def setline(self, line_num, s):
        c = self.code.split('\n')
        c[line_num] = s
        self.code = '\n'.join(c)

    def rmlines(self, a, b):
        c = self.code.split('\n')
        del c[a:b]
        self.code = '\n'.join(c)

    def show(self, highlight=None):
        h = None
        if highlight:
            h = highlighted(highlight)
        for i, line in enumerate(self.code.split('\n')):
            if h and highlight in line:
                line = line.replace(highlight, h)
            print str(i).rjust(3) + ': ' + line

    def commit(self):
        with open(self.filename, 'w') as f:
            f.write(self.code)

@list_files
def get_code(s):
    return Code(s.pop())

def get_extern():
    return get_code(externs)

def get_inset():
    return get_code(insets)

if __name__ == '__main__':
    print_externs()
    print_insets()
