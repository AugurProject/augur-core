#!/bin/bash

set -e

echo "Deploying Augur..."

export ETHEREUM_HOST="ropsten.augur.net"
export ETHEREUM_PORT="8545"
export ETHEREUM_PRIVATE_KEY=$ROPSTEN_PRIVATE_KEY

#docker container run -e ETHEREUM_HOST -e ETHERUM_PORT -e ETHEREUM_PRIVATE_KEY -it augur/core-deploy:latest
node output/deployment/deployContracts.js
