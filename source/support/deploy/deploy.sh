#!/bin/bash

if [[ "${DEPLOY:-true}" == "true" ]]; then
  node ./output/deployment/deployNetworks.js $@
  if [[ "$?" != "0" ]]; then
    echo "Error while deploying contracts to $ETHEREUM_NETWORK, exiting and skipping artifact management"
    exit 1
  fi
else
  echo "Skipping deploy, set DEPLOY=true to do it"
fi

