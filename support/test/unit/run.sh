#!/bin/bash

set -e

echo "Starting Solidity Linting..."
docker run --rm -it --entrypoint=npx augur/augur-core-test:latest solium --dir . --reporter=gcc
echo "Done Solidity Linting..."

if [[ "$1" == "console" ]]; then
  docker run --rm -it --entrypoint /bin/bash augur/augur-core-test:latest
else
  docker run --rm -it augur/augur-core-test:latest
fi
