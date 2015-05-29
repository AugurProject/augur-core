import bsddb
import json

db = bsddb.hashopen('build')
data_and_api = 'cash info branches events expiringEvents fxMath markets reporting whitelist'.split(' ')
functions = 'checkQuorum buy&sellShares createBranch p2pWagers sendReputation transferShares makeReports createEvent createMarket closeMarket closeMarketOne closeMarketTwo closeMarketFour closeMarketEight dispatch'.split(' ')
consensus = 'statistics interpolate center score adjust resolve payout redeem_interpolate redeem_center redeem_score redeem_adjust redeem_resolve redeem_payout'.split(' ')

for name, value in globals().items():
    if type(value) == list:
        print name.replace('_', ' ').capitalize()
        print '-'*len(name)
        print
        print 'contract | address'
        print '---------|--------'
        for contract in value:
            print contract, '|', json.loads(db[contract])['address']
        print
