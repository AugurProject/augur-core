#!/bin/bash

set -e

echo "Starting Solidity Linting..."
docker container run --entrypoint=solium augur/core-test:latest --dir src --reporter=gcc
echo "Done Solidity Linting..."
docker container run augur/core-test:latest
