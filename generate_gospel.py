#!/usr/bin/env python
"""the gospel according to ChrisCalderon"""
import sys
import getopt
import json
from pyrpctools import DB

data_and_api = 'cash info branches events expiringEvents fxpFunctions markets reporting'.split(' ')
functions = 'checkQuorum buy&sellShares createBranch p2pWagers sendReputation transferShares makeReports createEvent createMarket closeMarket closeMarketOne closeMarketTwo closeMarketFour closeMarketEight dispatch'.split(' ')
consensus = 'statistics interpolate center score adjust resolve payout redeem_interpolate redeem_center redeem_score redeem_adjust redeem_resolve redeem_payout'.split(' ')

def gospelify(output="md"):
    if output == "json":
        print "{"
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
                if name != "consensus":
                    print
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
    gospelify(output=output)

if __name__ == '__main__':
    sys.exit(main())
