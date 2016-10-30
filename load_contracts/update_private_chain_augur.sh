#!/bin/bash

ssh jack@45.33.62.72 sudo service augur stop
ssh jack@45.33.62.72 rm -Rf /home/jack/augur/build
scp -rp $HOME/src/augur/build jack@45.33.62.72:/home/jack/augur/build
ssh jack@45.33.62.72 cp /home/jack/augur/src/env-9000.json /home/jack/augur/build/env.json
ssh jack@45.33.62.72 sudo service augur start
