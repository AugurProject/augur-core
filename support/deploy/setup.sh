#!/bin/bash

echo "Building deploy image"
docker image build --tag augur/augur-core-deploy:latest --file ./support/deploy/Dockerfile .
