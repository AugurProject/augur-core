#!/bin/bash

ssh jack@45.33.62.72 -t "cd /home/jack/augur && /home/jack/augur/update-local.sh && cp /home/jack/augur/src/env-9000.json /home/jack/augur/build/config/env.json && sudo service augur restart"
