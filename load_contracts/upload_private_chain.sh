#!/bin/bash
# AUGUR_CONTRACTS=~/src/augur-contracts AUGURJS=~/src/augur.js
# @author Jack Peterson (jack@tinybike.net)

set -e

ssh jack@45.33.62.72 sudo service geth stop
ssh jack@45.33.62.72 rm -Rf /home/jack/.ethereum-9000/geth/chaindata
scp -rp $HOME/.ethereum-9000/geth/chaindata jack@45.33.62.72:/home/jack/.ethereum-9000/geth/chaindata
ssh jack@45.33.62.72 sudo service geth start
ssh jack@45.33.62.72 sudo service augur stop
ssh jack@45.33.62.72 rm -Rf /home/jack/augur/build
scp -rp $HOME/src/augur/build jack@45.33.62.72:/home/jack/augur/build
ssh jack@45.33.62.72 cp /home/jack/augur/src/env-9000.json /home/jack/augur/build/config/env.json
ssh jack@45.33.62.72 sudo service augur start

