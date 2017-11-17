#!/bin/bash

set -e

echo "Starting Solidity Linting..."
docker run --rm -it --entrypoint=npx augurproject/augur-core-test:latest solium --dir . --reporter=gcc
echo "Done Solidity Linting..."

if [[ "$1" == "console" ]]; then
  docker run --rm -it --entrypoint /bin/bash augurproject/augur-core-test:latest
else
  docker run --rm -it augurproject/augur-core-test:latest
fi
