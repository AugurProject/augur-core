#!/bin/bash

set -e

echo "Deploying Augur to $2"

port="8545"
case $2 in
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
    ;;
  *)
    echo "Must specify a network to deploy"
    exit 1
    ;;
esac

case $1 in
  "docker")
    docker container run -rm -it \
      -e AUGUR_CONTROLLER_ADDRESS=$controller \
      -e ETHEREUM_GAS_PRICE_IN_NANOETH=$gasPrice \
      -e ETHEREUM_HOST=$host \
      -e ETHEREUM_PORT=$port \
      -e ETHEREUM_PRIVATE_KEY=$privateKey \
      --entrypoint "bash /app/deploy.sh"
      augur/core-deploy:latest
    ;;
  "direct")
    node output/deployment/compileContracts.js
    AUGUR_CONTROLLER_ADDRESS=$controller ETHEREUM_GAS_PRICE_IN_NANOETH=$gasPrice ETHEREUM_HOST=$host ETHEREUM_PORT=$port ETHEREUM_PRIVATE_KEY=$privateKey support/deploy/deploy.sh
    ;;
  *)
    echo "Must specifiy either docker or direct as first argument"
    exit 1
    ;;
esac

exit

