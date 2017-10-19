#!/bin/bash

# make it so we can do job control inside the script (fg at the end)
set -m

# geth is dumb and won't let us run it in the background, and nohup redirects to file when run in a script
tail -F nohup.out &

#TODO: Create a config file (if possible) rather than using command line parameters
nohup geth --datadir /geth/chain --keystore /geth/keys --password /geth/password.txt --verbosity 2 --unlock "0xc5ed899b0878656feb06467e2e9ede3ae73cbcb7" --mine --ws --wsapi eth,net,web3,personal --wsport 8546 --rpc --rpcapi eth,net,web3,personal,miner --rpcaddr 0.0.0.0 --targetgaslimit 6500000 &

# spin until node is connectable
while ! curl --silent --show-error localhost:8545 -H "Content-Type: application/json" -X POST --data '{"jsonrpc":"2.0","method":"net_version","id": 1}'; do sleep 0.1; done
curl --silent --show-error localhost:8545 -H "Content-Type: application/json" -X POST --data '{"jsonrpc":"2.0","method":"eth_sendTransaction","params":[{"value":"0x0","to":"0x0000000000000000000000000000000000000000","from":"0xc5ed899b0878656feb06467e2e9ede3ae73cbcb7","data":"0x","gasPrice":"0x1"}], "id": 1}'

# bring geth to the foreground
fg
