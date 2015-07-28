#!/usr/bin/env python
"""the gospel according to ChrisCalderon"""
import os
import sys
import getopt
import json
from pyrpctools import DB

ROOT = os.path.dirname(os.path.realpath(__file__))
SRCPATH = os.path.join(ROOT, 'src')

data_and_api = 'cash info branches events expiringEvents fxpFunctions markets reporting'.split(' ')
functions = 'checkQuorum buy&sellShares createBranch p2pWagers sendReputation transferShares makeReports createEvent createMarket closeMarket closeMarketOne closeMarketTwo closeMarketFour closeMarketEight dispatch faucets'.split(' ')
consensus = 'statistics center score adjust resolve payout redeem_interpolate redeem_center redeem_score redeem_adjust redeem_resolve redeem_payout'.split(' ')

def read_gospel(gospel_path):
    with open(gospel_path) as json_file:
        gospel = json.load(json_file)
    return gospel    

# copy addresses from build.json file to leveldb
def leveldbify(gospel):
    for name, data in gospel.items():
        DB.Put(name, json.dumps(data))

# verify addresses were stored correctly
def test_leveldbify(gospel):
    for name, data in gospel.items():
        assert data == json.loads(DB.Get(name))

def gospelify(output="md"):
    if output == "json":
        print "{"
        print '    "namereg": "0xc6d9d2cd449a754c494264e1809c50e34d64562b",'
    for name, value in reversed(sorted(globals().items())):
        if type(value) == list:
            if output == "json":
                for i, contract in enumerate(value):
                    address = json.loads(DB.Get(contract))['address']
                    if contract == "buy&sellShares":
                        contract = "buyAndSellShares"
                    outstr = '    "' + contract + '": "' + address + '"'
                    if name != "consensus" or i < len(value) - 1:
                        outstr += ","
                    outstr += "\n"
                    sys.stdout.write(outstr)
                    sys.stdout.flush()
            else:
                print name.replace('_', ' ').capitalize()
                print '-'*len(name)
                print
                print 'contract | address'
                print '---------|--------'
                for contract in value:
                    print contract, '|', json.loads(DB.Get(contract))['address']
                print
    if output == "json":
        print "}"

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        short_opts = 'hjd'
        long_opts = ['help', 'json', 'leveldb']
        opts, vals = getopt.getopt(argv[1:], short_opts, long_opts)
    except getopt.GetoptError as e:
        sys.stderr.write(e.msg)
        sys.stderr.write("for help use --help")
        return 2
    output = "md"
    to_leveldb = False
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(__doc__)
            return 0
        elif opt in ('-j', '--json'):
            output = "json"
        elif opt in ('-d', '--leveldb'):
            to_leveldb = True
    if to_leveldb:
        gospel = read_gospel(os.path.join(ROOT, "build.json"))
        leveldbify(gospel)
        test_leveldbify(gospel)
    else:
        gospelify(output=output)

if __name__ == '__main__':
    sys.exit(main())
