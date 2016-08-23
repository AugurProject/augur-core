#!/bin/bash
# An everything-included contract updater that is set up specifically for Jack's local
# environment. Third parties, use this at your own peril :P
# @author Jack Peterson (jack@tinybike.net)

set -e

if [ "$#" -eq 1 ]; then
    ./load_contracts.py --contract $1
else
    ./load_contracts.py
fi
./generate_gospel.py -i ~/src/augur-contracts/contracts.json -o ~/src/augur-contracts/contracts.json
./make_api.py -i ~/src/augur-contracts/api.json -o ~/src/augur-contracts/api.json
if [ "$#" -ne 1 ]; then
    ~/src/augur.js/scripts/new-contracts.js
    ~/src/augur.js/scripts/canned-markets.js
fi
