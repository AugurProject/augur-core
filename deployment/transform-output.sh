#!/bin/bash

dotsunited-merge-json $1/addresses.json $1/addresses.json $2/addresses.json > $2/addresses.json
cat $1/contracts.json | jqn --color=false -j "at('contracts') | map(values) | flatten | map(mapValues(get('abi'))) | reduce(merge, {})" > $2/abi.json
