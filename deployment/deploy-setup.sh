#!/bin/bash

echo "Building deploy image"
docker image build --tag augur/core-deploy:latest --file Dockerfile-deploy .
