#!/bin/bash

set -e

echo "Deploying Augur..."

export ETHEREUM_HOST="ropsten.augur.net"
export ETHEREUM_PORT="8546"
export ETHEREUM_PRIVATE_KEY=$ROPSTEN_PRIVATE_KEY
docker container run -e ETHEREUM_HOST -e ETHERUM_PORT -e augur/core-deploy:latest
