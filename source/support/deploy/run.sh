#!/bin/bash

set -e

environment=$1
shift

case "$environment" in
  "docker")
    docker run --rm -it \
      --env-file <(env | grep "PRIVATE_KEY\|TRAVIS\|TOKEN") \
      -e DEPLOY \
      -e ARTIFACTS \
      --entrypoint "node"  \
      augurproject/augur-core:latest -- /app/output/deployment/deployNetworks.js $@
    ;;
  "direct")
    echo "Deploying to $@"
    node ./output/deployment/deployNetworks.js $@
    ;;
  *)
    echo "Must specifiy either docker or direct as first argument"
    exit 1
    ;;
esac

