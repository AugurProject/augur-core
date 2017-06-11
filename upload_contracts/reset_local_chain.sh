#!/bin/bash
# AUGUR_CONTRACTS=~/src/augur-contracts AUGURJS=~/src/augur.js
# @author Jack Peterson (jack@tinybike.net)

set -e
geth --datadir $HOME/.ethereum-10101 removedb
geth --datadir $HOME/.ethereum-10101 init $AUGURJS/data/genesis-10101.json
geth --mine --minerthreads 1 --ws --wsapi eth,net,web3,admin,personal,miner,txpool --wsport 8546 --wsorigins '*' --cache 2048 --networkid 10101 --datadir $HOME/.ethereum-10101 --rpc --rpcapi eth,net,web3,admin,personal,miner,txpool --rpccorsdomain '*' --maxpeers 128 --etherbase 0x05ae1d0ca6206c6168b42efcd1fbe0ed144e821b --unlock 0x05ae1d0ca6206c6168b42efcd1fbe0ed144e821b --password $HOME/.ethereum-10101/.password &
gethpid=$!
sleep 5
./upload_to_chain.js
./make_api.py -i $AUGUR_CONTRACTS/api.json -o $AUGUR_CONTRACTS/api.json
$AUGURJS/scripts/canned-markets.js
sleep 5
kill $gethpid
