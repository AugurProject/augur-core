#!/bin/bash

set -e

echo "Starting Solidity Linting..."
docker container run --entrypoint=npx augur/core-test:latest solium --dir src --reporter=gcc
echo "Done Solidity Linting..."
docker container run augur/core-test:latest
