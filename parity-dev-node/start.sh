#!/bin/bash

# make it so we can do job control inside the script (fg at the end)
set -m

# launch parity in the background
/parity/parity --config /parity/instant-seal-config.toml --gasprice 1 &

# spin until node is connectable
while ! curl --silent --show-error localhost:8545 -H "Content-Type: application/json" -X POST --data '{"jsonrpc":"2.0","method":"net_version","id": 1}'; do sleep 0.1; done
curl --silent --show-error localhost:8545 -H "Content-Type: application/json" -X POST --data '{"jsonrpc":"2.0","method":"eth_sendTransaction","params":[{"value":"0x0","to":"0x0000000000000000000000000000000000000000","from":"0x913da4198e6be1d5f5e4a40d0667f70c0b5430eb","data":"0x","gasPrice":"0x3B9ACA00"}], "id": 1}'

# bring parity to the foreground
fg
