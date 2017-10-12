#!/bin/bash

# make it so we can do job control inside the script (fg at the end)
set -m

# launch parity in the foreground
/parity/parity \
	--chain dev \
	--gasprice 2 \
	--no-discovery \
	--force-ui --ui-no-validation --ui-interface 0.0.0.0 \
	--jsonrpc-interface all --jsonrpc-cors "*" --jsonrpc-hosts all --jsonrpc-apis web3,eth,net,personal,parity,parity_set,traces,rpc,parity_accounts \
	--unlock 0x00a329c0648769a73afac7f9381e08fb43dbea72 --password /parity/password \
	&

# spin until node is connectable
while ! curl --silent --show-error localhost:8545 -H "Content-Type: application/json" -X POST --data '{"jsonrpc":"2.0","method":"net_version","id": 1}'; do sleep 0.1; done
curl --silent --show-error localhost:8545 -H "Content-Type: application/json" -X POST --data '{"jsonrpc":"2.0","method":"eth_sendTransaction","params":[{"value":"0x0","to":"0x0000000000000000000000000000000000000000","from":"0x00a329c0648769a73afac7f9381e08fb43dbea72","data":"0x","gasPrice":"0x3B9ACA00"}], "id": 1}'
fg
