#!/bin/bash

if [[ "$TRAVIS" == "true" ]]; then
  if [[ "$TRAVIS_PULL_REQUEST" != "false" ]]; then
    echo "Skipping updating augur-contracts for pull request ${TRAVIS_PULL_REQUEST}"
    exit
  fi

  branch=$TRAVIS_BRANCH
  tag=$TRAVIS_TAG
  commit=$TRAVIS_COMMIT
  repo_url=https://$GITHUB_DEPLOYMENT_TOKEN@github.com/AugurProject/augur-contracts
else
  branch=$(git rev-parse --abbrev-ref HEAD)
  commit=$(git rev-parse --short HEAD)
  tag=$(git name-rev --tags --name-only $(git rev-parse HEAD) | sed "s/\^0//")
  if [[ "${tag}" != "undefined" ]]; then
    branch=$tag
  else
    tag=''
  fi

  if [[ "${AUGUR_CONTRACTS_REPO_URL}x" == "x" ]]; then
    repo_url=https://github.com/AugurProject/augur-contracts
    echo "AUGUR_CONTRACTS_REPO_URL not set, defaulting to ${repo_url}"
  else
    repo_url=$AUGUR_CONTRACTS_REPO_URL
  fi
fi

git clone $repo_url output/augur-contracts
current_dir=$PWD;
cd output/augur-contracts
git checkout -b paul origin/paul
npm install

  BRANCH=$branch COMMIT=$commit TAG=$tag SOURCE=../contracts npm run update-contracts
update_success=$?
cd $current_dir

exit $update_success
