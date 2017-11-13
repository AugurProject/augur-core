#!/bin/bash

set -e

echo "Deploying Augur to $1"

port="8545"
inspect="" #"--inspect--brk"

case $1 in
  "ropsten")
    host="ropsten.augur.net"
    privateKey=$ROPSTEN_PRIVATE_KEY
    gasPrice=20
    ;;
  "rinkeby")
    host="rinkeby.augur.net"
    privateKey=$RINKEBY_PRIVATE_KEY
    gasPrice=20
    controller="0xa76ecf40e366d3462a857cbb4695158e4601a8f6"
    ;;
  "kovan")
    host="kovan.augur.net"
    privateKey=$KOVAN_PRIVATE_KEY
    gasPrice=1
    ;;
  "rockaway")
    host="localhost"
    privateKey=$ROCKAWAY_PRIVATE_KEY
    gasPrice=1
esac

AUGUR_CONTROLLER_ADDRESS=$controller ETHEREUM_GAS_PRICE_IN_NANOETH=$gasPrice ETHEREUM_HOST=$host ETHEREUM_PORT=$port ETHEREUM_PRIVATE_KEY=$privateKey node $inspect output/deployment/compileAndDeploy.js

exit

docker container run -it \
  -e AUGUR_CONTROLLER_ADDRESS=$controller \
  -e ETHEREUM_GAS_PRICE_IN_NANOETH=$gasPrice \
  -e ETHEREUM_HOST=$host \
  -e ETHEREUM_PORT=$port \
  -e ETHEREUM_PRIVATE_KEY=$privateKey \
  augur/core-deploy:latest
