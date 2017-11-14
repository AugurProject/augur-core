#!/bin/bash
node output/deployment/deployContracts.js

if [[ "$TRAVIS" == "true" ]];
  if [[ "$TRAVIS_PULL_REQUEST" != "false" ]]; then
    echo "Skipping updating augur-contracts for pull request ${TRAVIS_PULL_REQUEST}"
    exit
  fi

  branch=$TRAVIS_BRANCH
  commit=$TRAVIS_COMMIT
  repo_url=https://$GITHUB_DEPLOYMENT_TOKEN@github.com/AugurProject/augur-contracts
else
  branch=$(git rev-parse --abbrev-ref HEAD)
  commit=$(git rev-parse --short HEAD)
  repo_url=https://github.com/AugurProject/augur-contracts
fi

git clone $repo_url output/augur-contracts
cd output/augur-contracts
npm install
BRANCH=$branch COMMIT=$commit npm run update-contracts -- ../contracts
