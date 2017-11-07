#!/bin/bash

set -e

echo "Deploying Augur to $1"

port="8545"

case $1 in
  "ropsten")
    host="ropsten.augur.net"
    privateKey=$ROPSTEN_PRIVATE_KEY
    ;;
  "rinkeby")
    host="rinkeby.augur.net"
    privateKey=$RINKEBY_PRIVATE_KEY
    ;;
  "kovan")
    host="kovan.augur.net"
    privateKey=$KOVAN_PRIVATE_KEY
    ;;
  "rockaway")
    host="localhost"
    privateKey=$ROCKAWAY_PRIVATE_KEY
esac

#docker container run -e ETHEREUM_HOST -e ETHERUM_PORT -e ETHEREUM_PRIVATE_KEY -it augur/core-deploy:latest
ETHEREUM_HOST=$host ETHEREUM_PORT=$port ETHEREUM_PRIVATE_KEY=$privateKey node output/deployment/compileAndDeploy.js
