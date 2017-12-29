#!/bin/bash

set -e

echo "Deploying Augur to $2"

[[ "${ARTIFACTS}" == "true" ]] || ARTIFACTS=false

port="8545"
case $2 in
  "ropsten")
    host="ropsten.augur.net"
    privateKey=$ROPSTEN_PRIVATE_KEY
    gasPrice=20
    ;;
  "rinkeby")
    host="rinkeby.ethereum.nodes.augur.net"
    port="80"
    privateKey=$RINKEBY_PRIVATE_KEY
    gasPrice=20
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
  "clique")
    host="clique.ethereum.nodes.augur.net"
    port="80"
    privateKey="fae42052f82bed612a724fec3632f325f377120592c75bb78adfcceae6470c5a"
    gasPrice=1
    ;;
  "aura")
    host="aura.ethereum.nodes.augur.net"
    port="80"
    privateKey="47f49c399482f73143cadeb2db8938d3f249578bdc64cdcda4ecf1ee535a5c91"
    gasPrice=1
    ;;
  *)
    echo "Must specify a network to deploy"
    exit 1
    ;;
esac

case $1 in
  "docker")
    docker run --rm -it \
      -e ETHEREUM_GAS_PRICE_IN_NANOETH=$gasPrice \
      -e ETHEREUM_HOST=$host \
      -e ETHEREUM_PORT=$port \
      -e ETHEREUM_PRIVATE_KEY=$privateKey \
      -e DEPLOY=true \
      -e ARTIFACTS \
      -e GITHUB_DEPLOYMENT_TOKEN \
      -e NPM_TOKEN \
      -e TRAVIS \
      -e TRAVIS_BRANCH \
      -e TRAVIS_TAG \
      -e TRAVIS_COMMIT \
      -e TRAVIS_PULL_REQUEST \
      --entrypoint "bash"  \
      augurproject/augur-core:latest -- /app/support/deploy/deploy.sh
    ;;
  "direct")
    ETHEREUM_GAS_PRICE_IN_NANOETH=$gasPrice \
    ETHEREUM_HOST=$host \
    ETHEREUM_PORT=$port \
    ETHEREUM_PRIVATE_KEY=$privateKey \
    DEPLOY=true \
    ARTIFACTS=$ARTIFACTS \
      bash support/deploy/deploy.sh
    ;;
  *)
    echo "Must specifiy either docker or direct as first argument"
    exit 1
    ;;
esac

