#!/bin/bash
# AUGUR_CONTRACTS=~/src/augur-contracts AUGURJS=~/src/augur.js
# @author Jack Peterson (jack@tinybike.net)

set -e
geth --datadir $HOME/.ethereum-9000 removedb
geth --datadir $HOME/.ethereum-9000 init $AUGURJS/data/genesis-9000.json
geth --mine --minerthreads 2 --ws --wsapi eth,net,web3,admin,personal,miner,txpool --wsport 8546 --wsorigins '*' --cache 2048 --networkid 9000 --datadir $HOME/.ethereum-9000 --rpc --rpcapi eth,net,web3,admin,personal,miner,txpool --ipcapi admin,eth,debug,miner,net,txpool,personal,web3 --rpccorsdomain '*' --maxpeers 128 --etherbase 0x05ae1d0ca6206c6168b42efcd1fbe0ed144e821b --unlock 0x05ae1d0ca6206c6168b42efcd1fbe0ed144e821b --password $HOME/.ethereum-9000/.password &
gethpid=$!
sleep 5
./load_contracts.py --blocktime 2
./generate_gospel.py -i $AUGUR_CONTRACTS/contracts.json -o $AUGUR_CONTRACTS/contracts.json
./make_api.py -i $AUGUR_CONTRACTS/api.json -o $AUGUR_CONTRACTS/api.json
$AUGURJS/scripts/new-contracts.js
$AUGURJS/scripts/canned-markets.js
sleep 5
kill $gethpid
ssh jack@45.33.62.72 sudo service geth stop
ssh jack@45.33.62.72 rm -Rf /home/jack/.ethereum-9000/geth/chaindata
scp -rp $HOME/.ethereum-9000/geth/chaindata jack@45.33.62.72:/home/jack/.ethereum-9000/geth/chaindata
ssh jack@45.33.62.72 sudo service geth start
ssh jack@45.33.62.72 sudo service augur stop
ssh jack@45.33.62.72 rm -Rf /home/jack/augur/build
scp -rp $HOME/src/augur/build jack@45.33.62.72:/home/jack/augur/build
ssh jack@45.33.62.72 cp /home/jack/augur/src/env-9000.json /home/jack/augur/build/env.json
ssh jack@45.33.62.72 sudo service augur restart
