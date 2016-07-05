'''
A module for serpent tests without nonsense.

Motivation:
    I write a lot of python scripts for testing serpent code,
  and I've noticed a few things which bug the heck out of me.
  One is that the pyethereum EVM prints out nonsense when it
  runs a contract. I'd have to delve into it's source to figure
  out how to disable this "feature" and I'm too lazy for that.
  Another thing that bugs me is that the serpent module prints
  out warning nonsense that doesn't seem to be disablable.
  Which leads me to my hacky solution...

Method/Madness:
    The first part is to completely disable warning output. If
  something is going to break, I'd rather it just break and not
  complain about it so much and clutter my test output. So let's
  completely disable warnings! But that doesn't solve the whole
  problem, because some warnings are hard coded into the C++ code
  in the serpent module. The there is the EVM nonsense. To fix that
  I just redirect stdout to /dev/null, and define my own PRINT
  function that forces data to show in the terminal. And while I'm
  at it, I might as well throw() the usual imports in since every
  test script I write will import this module. And maybe I should
  define some useful contants and functions...
'''

# disable warning crud about eggs and whatnot
from warnings import simplefilter; simplefilter('ignore')
# tester module!
from ethereum import tester
import serpent
from cStringIO import StringIO 
import sys, os


t = tester
STDOUT = sys.stdout
REDIRECT = StringIO()
PASSED = 'TEST PASSED'
FAILED = 'TEST FAILED'
sys.stdout = REDIRECT #avoids nonsense when calling contract functions
TAB = ' '*3

#all caps cuz why not? :/
def PRINT(*args, **kwds):
    '''Use this function to print, as stdout is redirected to devnull.

All args have str called on them before they are "printed" to STDOUT.
Keyword arguments:
end  -- A string to append to the end of the printed args.
        This defaults to os.linesep.
seq  -- A string to join the arguments by. Default is ' '.
file -- A file-like object to use instead of STDOUT.
        Must have both write and flush methods.
    '''
    end = kwds.get('end', os.linesep)
    sep = kwds.get('sep', ' ')
    fileobj = kwds.get('file', STDOUT)
    outstr = sep.join(map(str, args))
    fileobj.write(outstr + end)
    fileobj.flush()

def _to_str(item):
    if type(item) == float:
        return '%.6f'%item
    else:
        return str(item)

class SimpleTable(object):
    '''A class for easily making tables and printing them.

Tables have a title, column labels, and rows:
+----------+----------+----------+
|           Table Test           |
+----------+----------+----------+
+----------+----------+----------+
|  LabelA  |  LabelB  |  LabelC  |
+----------+----------+----------+
|1371032652| 666555510|9814208081|
+----------+----------+----------+
|1191656453|7918551629|6032785125|
+----------+----------+----------+
|1952864215|6186265278|3779520336|
+----------+----------+----------+


  The rows of a table can also be 'labeled', by having the
first column label be the empty string, and each rows 'label'
be the first element of the row:
+----+----------+----------+----------+
|             Table Test 2            |
+----+----------+----------+----------+
+----+----------+----------+----------+
|    |  LabelA  |  LabelB  |  LabelC  |
+----+----------+----------+----------+
|row0|1371032652| 666555510|9814208081|
+----+----------+----------+----------+
|row1|1191656453|7918551629|6032785125|
+----+----------+----------+----------+
|row2|1952864215|6186265278|3779520336|
+----+----------+----------+----------+
    '''

    def __init__(self, title, column_labels):
        self.title = title
        self.labels = map(str, column_labels)
        self.rows = []
        self.widths = map(len, self.labels)
        self.file = STDOUT
        self.final_message = None
        
    def add_row(self, row):
        '''Appends a row to the table.'''
        assert len(row) == len(self.labels), 'not enough columns in the row!'
        self.rows.append(map(_to_str, row))
        self.widths = map(max,
                          zip(self.widths, 
                              map(len, 
                                  self.rows[-1])))

    def set_file(self, fileobj):
        '''Sets the file object used for printing the table.'''
        self.file = fileobj

    def print_table(self):
        '''PRINTs table data prettily.'''

        def p(out):
            PRINT(out, file=self.file)
    
        bar, label_row = [''], ['']
        for width, label in zip(self.widths, self.labels):
            bar.append('-' * (width))
            label_row.append(str(label).center(width))
        bar.append(''); bar = '+'.join(bar)
        label_row.append(''); label_row = '|'.join(label_row)

        p('+' + '-'*(len(bar) - 2) + '+')
        p('|' + self.title.center(len(bar) - 2) + '|')
        p('+' + '-'*(len(bar) - 2) + '+')

        p(bar)
        p(label_row)
        p(bar)

        for row in self.rows:
            adjusted_row = ['']
            for width, item in zip(self.widths, row):
                adjusted_row.append(str(item).rjust(width))
            adjusted_row.append('')
            p('|'.join(adjusted_row))
            p(bar)

        if self.final_message:
            p(bar)
            p('+' + self.final_message.center(len(bar) - 2) + '+')
            p(bar)

def main():
    import random
    table = SimpleTable('Table Test',
                  ['LabelA', 'LabelB', 'LabelC'])

    for i in range(3):
        row = []
        for j in range(3):
            row.append(random.randrange(10**10))
        table.add_row(row)

    table.print_table()

    PRINT()
    
    named_rows = SimpleTable(table.title + ' 2',
                       [''] + table.labels)

    for i, row in enumerate(table.rows):
        named_rows.add_row(['row%d'%i] + row)
    
    named_rows.print_table()

if __name__ == '__main__':
    main()
