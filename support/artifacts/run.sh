#!/bin/bash -x

###
# Setup the environments properly for merging and updating items in augur-contracts and augur.js
# a lot of this is because we need to rely on Travis environment because it checks out in a
# detached head state so we don't good branch information out of our local git repo


if [[ "$TRAVIS" == "true" ]]; then
  if [[ "$TRAVIS_PULL_REQUEST" != "false" ]]; then
    echo "Skipping updating augur-contracts for pull request ${TRAVIS_PULL_REQUEST}"
    exit
  fi

  git config --global user.email "team@augur.net"
  git config --global user.name "Augur CI"
  git config --global push.default "simple"

  branch=$TRAVIS_BRANCH
  tag=$TRAVIS_TAG
  commit=$TRAVIS_COMMIT
  contracts_repo_url=https://$GITHUB_DEPLOYMENT_TOKEN@github.com/AugurProject/augur-contracts
  augurjs_repo_url=https://$GITHUB_DEPLOYMENT_TOKEN@github.com/AugurProject/augur.js
else
  branch=$(git rev-parse --abbrev-ref HEAD)
  commit=$(git rev-parse --short HEAD)
  tag=$(git name-rev --tags --name-only $(git rev-parse HEAD) | sed "s/\^0//")
  if [[ "${tag}" != "undefined" ]]; then
    branch=$tag
  else
    tag=''
  fi

  contracts_repo_url=${AUGUR_CONTRACTS_REPO_URL:-https://github.com/AugurProject/augur-contracts}
  echo "AUGUR_CONTRACTS_REPO_URL=${contracts_repo_url}, set environment to override"

  augurjs_repo_url=${AUGURJS_REPO_URL:-https://github.com/AugurProject/augur.js}
  echo "AUGURJS_REPO_URL=${augurjs_repo_url}, set environment to override"

  rm -rf output/augur-contracts
  rm -rf output/augur.js
fi

if [[ -e "$HOME/.npmrc" ]]; then
  echo "Using exisiting .npmrc"
elif [[ -e "$HOME/.npmrc.deploy" && "${NPM_TOKEN}x" != "x" ]]; then
  echo "Using NPM_TOKEN to create ~/.npmrc"
  cp ~/.npmrc.deploy ~/.npmrc
else
  echo "No logged in NPM session and NPM_TOKEN not set, will not be able to publish to NPM"
fi


###
# Update the augur-contracts Repository

git clone $contracts_repo_url output/augur-contracts
current_dir=$PWD
cd output/augur-contracts

npm install

AUTOCOMMIT=true BRANCH=$branch COMMIT=$commit TAG=$tag SOURCE=../contracts npm run update-contracts
update_success=$?

contracts_version=$(npm version)
cd $current_dir

[[ $update_success == 0 ]] || exit $update_success


###
# Update the augur.js repository

git clone $augurjs_repo_url output/augur.js
current_dir=$PWD
cd output/augur.js

AUTOCOMMIT=true BRANCH=$branch COMMIT=$commit TAG=$tag npm run update-contracts
update_success=$?

cd $current_dir

exit ${update_success}
