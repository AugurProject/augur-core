#!/bin/bash

set -e

echo "Starting Solidity Linting..."
docker container run --entrypoint=npx augur/core-test:latest solium --dir . --reporter=gcc
echo "Done Solidity Linting..."

if [[ "$1" == "console" ]]; then
  docker container run --rm -it --entrypoint /bin/bash augur/core-test:latest
else
  docker container run augur/core-test:latest
fi
