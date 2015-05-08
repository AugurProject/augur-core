#!/usr/bin/python
import os
externs = set()
macros = set()
for dir_, subdirs, files in os.walk('src'):
    for filename in files:
        if filename.endswith('.se'):
            code = open(os.path.join(dir_, filename))
            for line in code:
                if line.startswith('extern'):
                    externs.add(code.name)
                if line.startswith('inset'):
                    macros.add(code.name)
print 'externs:'
for i in externs:
    print ' '*4+i
print 'insets:'
for i in macros:
    print ' '*4+i
