#!/usr/bin/env python
"""The Augur contract gospel.

Generates a "gospel" of Ethereum addresses for the Augur contracts:
https://github.com/AugurProject/augur-contracts/blob/master/contracts.json

Usage:

    python generate_gospel.py [flags]

Optional flags:

    -i, --inpath [/path/to/input/contracts.json]:
        Local filesystem path to augur-contracts/contracts.json.

    -o, --outpath [/path/to/output/contracts.json]:
        Local path where the updated contracts.json will be written.
        If no output path is specified, the updated gospel is sent to stdout.
        (Warning: if this file exists, it will be overwritten.)

    -n, --networkid [network ID]:
        Ethereum network ID.  If no network ID is specified, this script
        will attempt to request the current ID from geth.  If no geth
        instance is found, defaults to '2' (Morden testnet).

@authors Chris Calderon (chris@augur.net) and Jack Peterson (jack@tinybike.net)

"""
import os
import sys
import getopt
import json
import requests
from pyrpctools import get_db, save_db, ROOT, RPC_Client

DB = get_db()
SOURCE = os.path.join(ROOT, os.pardir, "src")
RPCHOST = "127.0.0.1"
RPCPORT = 8545
DEFAULT_NETWORK_ID = "2"
CONTRACTS_URL = "https://raw.githubusercontent.com/AugurProject/augur-contracts/master/contracts.json"

def make_groups():
    groups = {}
    for directory, subdirs, files in os.walk(SOURCE):
        if files:
            group_name = os.path.basename(directory).title()
            name_list = []
            for f in files:
                if f.endswith(".se"):
                    shortname = f[:-3]
                    if shortname in DB:
                        name_list.append(shortname)
            name_list.sort()
            groups[group_name] = name_list
    return groups

def generate_gospel_from_db():
    gospel = {}
    for name, value in reversed(sorted(make_groups().items())):
        for i, contract in enumerate(value):
            address = DB[contract]["address"]
            if contract == "buy&sellShares": contract = "buyAndSellShares"
            contract = contract[0].upper() + contract[1:]
            gospel[contract] = address
    return gospel

def get_local_contracts(path):
    print("Read contract addresses from: " + path)
    with open(path, "r") as in_file:
        contracts = json.load(in_file)
    return contracts

def get_remote_contracts(url):
    print("Download contracts.json: " + url)
    response = requests.get(url)
    if response.status_code == 200:
        try:
            return response.json()
        except Exception as exc:
            print(exc)

def get_contracts(path):
    if path is not None: return get_local_contracts(path)
    return get_remote_contracts(CONTRACTS_URL)

def get_network_id(rpc_host, rpc_port):
    return RPC_Client((RPCHOST, RPCPORT), 0).net_version()["result"]

def write_contracts(path, contracts):
    print("Write contract addresses to: " + path)
    with open(path, "w") as out_file:
        json.dump(contracts, out_file, indent=4, sort_keys=True)

def update_contracts(in_path=None, out_path=None,
                     rpc_host=RPCHOST, rpc_port=RPCPORT, network_id=None):
    gospel = generate_gospel_from_db()
    contracts = get_contracts(in_path)
    
    id_requested = network_id 

    #gospel is the contracts from the current_network_id. if a different id 
    #is passed in, validate it and replace gospel with those from contracts[network_id]
    current_network_id = get_network_id(rpc_host, rpc_port);
    if network_id is None:
        network_id = current_network_id
    elif network_id != current_network_id:
        if network_id in contracts:
            gospel = contracts[network_id]
        else:
            print("Network ID: " + str(network_id) + " not found. Using default");
            network_id = DEFAULT_NETWORK_ID

    print("Network ID: " + str(network_id))

    if contracts and out_path is not None:
        if id_requested is not None:
            write_contracts(out_path, gospel)
        else:
            #if -o used w/out -n, write out addressed for all networkIDs
            contracts[network_id] = gospel
            write_contracts(out_path, contracts)
    else:
        print(json.dumps(gospel, indent=4, sort_keys=True))

def main(argv=None):
    if argv is None: argv = sys.argv
    try:
        short_opts = "hjn:i:o:"
        long_opts = ["help", "json", "networkid=", "infile=", "outfile="]
        opts, vals = getopt.getopt(argv[1:], short_opts, long_opts)
    except getopt.GetoptError as e:
        sys.stderr.write(e.msg)
        sys.stderr.write("for help use --help")
        return 2
    in_path, out_path, network_id = None, None, None
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(__doc__)
            return 0
        elif opt in ("-i", "--infile"):
            in_path = arg
        elif opt in ("-j", "--json"):
            print("\n***Warning: -j (--json) option is deprecated***\n")
        elif opt in ("-o", "--outfile"):
            out_path = arg
        elif opt in ("-n", "--networkid"):
            network_id = arg
    update_contracts(in_path=in_path,
                     out_path=out_path,
                     rpc_host=RPCHOST,
                     rpc_port=RPCPORT,
                     network_id=network_id)
    return 0

if __name__ == "__main__":
    sys.exit(main())
