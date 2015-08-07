#!/usr/bin/env python
"""the gospel according to ChrisCalderon"""
import os
import sys
import getopt
import json
from pyrpctools import get_db, save_db, ROOT

DB = get_db()
SOURCE = os.path.join(ROOT, 'src')

def make_groups():
    groups = {}
    for directory, subdirs, files in os.walk(SOURCE):
        if files:
            group_name = os.path.basename(directory).title()
            name_list = []
            for f in files:
                if f.endswith('.se'):
                    shortname = f[:-3]
                    if shortname in DB:
                        name_list.append(shortname)
            name_list.sort()
            groups[group_name] = name_list
    return groups

def gospelify(output):
    if output == "json":
        print "{"
        print '    "namereg": "0xc6d9d2cd449a754c494264e1809c50e34d64562b",'
    for name, value in reversed(sorted(make_groups().items())):
        if output == "json":
            for i, contract in enumerate(value):
                address = DB[contract]['address']
                if contract == "buy&sellShares":
                    contract = "buyAndSellShares"
                outstr = '    "' + contract + '": "' + address + '"'
                if name != "consensus" or i < len(value) - 1:
                    outstr += ","
                outstr += "\n"
                sys.stdout.write(outstr)
                sys.stdout.flush()
        else:
            print name
            print '-'*len(name)
            print
            print 'contract | address'
            print '---------|--------'
            for contract in value:
                print contract, '|', DB[contract]['address']
            print
    if output == "json":
        print "}"

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        short_opts = 'hj'
        long_opts = ['help', 'json']
        opts, vals = getopt.getopt(argv[1:], short_opts, long_opts)
    except getopt.GetoptError as e:
        sys.stderr.write(e.msg)
        sys.stderr.write("for help use --help")
        return 2
    output = "md"
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(__doc__)
            return 0
        elif opt in ('-j', '--json'):
            output = "json"
    else:
        gospelify(output)
        return 0

if __name__ == '__main__':
    sys.exit(main())
