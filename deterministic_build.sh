#!/bin/bash
# takes controller address as first param, can hardcode to the latest one post launch

FILES="$(find src -name '*.se')"
rm -rf compiled
mkdir compiled
python upload_contracts/upload_contracts.py update -s src/ -c "$1"
for i in $FILES
do
    b=$( basename "$i" )
    echo $i
    serpent compile $i > compiled/$b.evm
    serpent mk_full_signature $i > compiled/$b.json
done