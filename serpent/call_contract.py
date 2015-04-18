#!/usr/bin/python
import warnings; warnings.simplefilter('ignore')
from load_contract import GethRPC
from pyepm.api import abi_data
from colorama import init, Style, Fore
import json
import sys
import re

contracts = {
    'cash' : '0x559b098076d35ddc7f5057bf28eb20d9cf183a99',
    'info' : '0x84ad0e89dbbbdfb18a59954addf10ad501525a01',
    'branches' : '0x2440e4769deb9fd3fd528884b95dc76e4e3482cf',
    'events' : '0xe34fd8a3840cba70fdd73a01c75302de959aa5a9',
    'expiringEvents' : '0xb7b617b776e66cbae79606d2b6221501ad110090',
    'fxpFunctions' : '0x82695a58b84bbcc90372d06e9b1d599ca2dd60cd',
    'markets' : '0x9d8b4e6da4e917e7b951f372e66b1012b203e30e',
    'reporting' : '0x175d90d83deec9e5b75cef6b0659958fe2fd24b1',
    'checkQuorum' : '0xdb609952cc948372d85081665d176d2c506c3591',
    'buy&sellShares' : '0xd89134277d395df906b06c2a7677fd97106bac6d',
    'createBranch' : '0xb01164d8174e6ce6ea5589824dca4e0acb92d26d',
    'p2pWagers' : '0x8b504a36f5dcd5debab695bd9474d47693195141',
    'sendReputation' : '0x9ba9fd49e9398bb756e5bcc4d7daec5efcca42c8',
    'transferShares' : '0xda588186e874e3d39b3884367342e98d3df0dfc1',
    'makeReports' : '0xa66d31612c2e716ab9633a8ba886686b3777d99a',
    'createEvent' : '0x134ae8c13f9955c205da87ea49c4d21612ff5c14',
    'createMarket' : '0x31298c07334febd45584d24797ced02bc54777ca',
    'closeMarket' : '0xfd7baeaae87c0a9833d1d9840d8f4be554f4a9fa',
    'interpolate' : '0x13aad6f5573db896e589d2fdef22da8c5033141d',
    'center' : '0x63faff743ab0398524c08a435f94ceb91352ba58',
    'score' : '0x5c90e13b3cdfb498945f10b60b140259e06a2651',
    'adjust' : '0xa59e9d9b48f462135f7e971ab370d3e156fd3b37',
    'resolve' : '0x63faff743ab0398524c08a435f94ceb91352ba58',
    'payout' : '0x88cae18facdaa0f3d0839d3f8a8874f2fa8c54cf',
}

def get_sym(arg):
    if type(arg) in (int, long):
        return 'i'
    if type(arg) == list:
        return 'a'
    else:
        return 's'

if __name__ == '__main__':
    c = contracts[sys.argv[1]]
    func = sys.argv[2]
    args = map(eval, sys.argv[3:])
    sig = reduce(lambda a, b: a+get_sym(b), args, '')
    data = abi_data(func, sig, args)

    rpc = GethRPC()
    coinbase = rpc.eth_coinbase()['result']
    result = rpc.eth_sendTransaction(
        sender=coinbase, gas=hex(3*10**4), to=c, data=data)
    print json.dumps(result, sort_keys=True, indent=4)
    print json.dumps(rpc.eth_getTransactionByHash(result['result']),
                     sort_keys=True,
                     indent=4)
    print json.dumps(rpc.eth_call('pending', sender=coinbase, to=c, data=data),
                     sort_keys=True,
                     indent=4)
