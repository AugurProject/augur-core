#!/bin/bash

set -e

echo "Starting Solidity Linting..."
docker container run --entrypoint=npx augur/core-test:latest solium --dir . --reporter=gcc
echo "Done Solidity Linting..."
docker container run augur/core-test:latest
