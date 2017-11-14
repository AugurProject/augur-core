git clone https://github.com/AugurProject/augur-contracts ./augur-contracts

node output/deployment/deployContracts.js

#bash ./augur-contracts/scripts/transform-output.sh
npm install -g jq.node dotsunited-merge-json
bash ./transform-output.sh output/contracts
