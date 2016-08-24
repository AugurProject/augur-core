#!/bin/bash
# An everything-included contract updater that is set up specifically for Jack's local
# environment. Third parties, use this at your own peril :P
# AUGUR_CONTRACTS=~/src/augur-contracts AUGURJS=~/src/augur.js
# @author Jack Peterson (jack@tinybike.net)

set -e

if [ "$#" -eq 1 ]; then
    ./load_contracts.py --contract $1
else
    ./load_contracts.py --blocktime 4
fi
./generate_gospel.py -i $AUGUR_CONTRACTS/contracts.json -o $AUGUR_CONTRACTS/contracts.json
./make_api.py -i $AUGUR_CONTRACTS/api.json -o $AUGUR_CONTRACTS/api.json
if [ "$#" -ne 1 ]; then
    $AUGURJS/scripts/new-contracts.js
    $AUGURJS/scripts/canned-markets.js
fi
