#!/usr/bin/python
import bsddb
import json
import sys
db = bsddb.hashopen('build')
print json.loads(db[sys.argv[1]])['sig']
print json.loads(db[sys.argv[1]])['fullsig']
