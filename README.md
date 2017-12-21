# augur-core

[![Build Status](https://travis-ci.org/AugurProject/augur-core.svg)](https://travis-ci.org/AugurProject/augur-core)

Smart contracts for [Augur](https://augur.net), a decentralized prediction market platform on the [Ethereum](https://ethereum.org) blockchain.

## Installation

You need system-wide installations of Python 2.7.6+, Node.js 8+, and [Solidity 0.4.18](https://github.com/ethereum/solidity/releases/tag/v0.4.18).  (Or Docker; see below.)  Install the dependencies:

```bash
npm install npx
npm install
pip install -r requirements.txt
```

Note: on macOS, you need to use [virtualenv](https://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/) or [homebrew](https://brew.sh/) Python to work around System Integrity Protection.

## Deployment

Solidity contract deployment is handled by `ContractDeployer.ts` and the wrapper programs located in `source/deployment`.  This deployment framework allows for incremental deploys of contracts to a given controller (specified via a configuration option).  This allows us to deploy new contracts without touching the controller, effectively upgrading the deployed system in-place.

### Automated Rinkeby deployment via Travis CI

Travis CI is set up automatically deploy the contracts to the [Rinkeby testnet](https://www.rinkeby.io) after the tests run successfully.  These deployments happen on a tagged version (release or pre-release) of augur-core, pushes changes to [augur-contracts](https://github.com/AugurProject/augur-contracts), and updates augur.js to match that new version of augur-contracts.

1. Tag augur-core as needed for a versioned deploy, e.g for a pre-release deployment: `npm version prerelease`
2. CI will Build, Test, and Deploy the contracts
3. augur-contracts will automatically have a new dev-channel version published to NPM (augur-contracts@dev)
4. augur.js will automatically have a new dev-channel version published to NPM (augur.js@dev)
5. If this is a real release (i.e. we want to declare this fit for public consumption), augur-contracts and augur.js should be published manually to NPM with their next version numbers.
6. If this is a real release, augur-contracts and augur.js should be incremented to their NEXT release version number, and have the pre-release version -0 appended to them, and pushed to master.

### Local deployment

Deployment can be run in two modes, direct or Docker. In direct mode, the assumption is that the entire system has been built (TypeScript and Solidity), and there is a working Node.js environment locally. Furthermore, one must possess an account on the deployment target (e.g. Rinkeby testnet) which has enough ETH to cover the costs of the deployment. For the purposes of deploying to the testnets, those with access to the augur private testnet keys can deploy and update the existing contracts. For reference, these keys are stored in an encrypted git repository within the Augur Project's keybase team. If you need access, please inquire in the Augur Discord.

All deployment commands can be managed through scripts in package.json, and can be executed using `npm run <command>`.

### Manual Rinkeby deployment

Build and create compile artifacts:

```bash
npm run build
```

Deploy to Rinkeby and push build artifacts: This is *not* using the dockerized commands, so that your local git and npm envs are used for the deployment. If you need to use the dockerized version you will need to pass:

a. GITHUB_DEPLOYMENT_TOKEN - set to a valid OAUTH token that allows pushing to github
b. NPM_TOKEN - The auth token value from your ~/.npmrc after you've logged into NOM

```bash
RINKEBY_PRIVATE_KEY=$(cat ../keys/deploy_keys/rinkeby.prv) DEPLOY=true ARTIFACTS=true AUTOCOMMIT=true npm run deploy:rinkeby
```

### Updating augur-contracts

(Note: commands _in this section only_ should be run from your local augur-contracts folder, not from augur-core!)

Manual deployment generates artifacts in the `output/contracts` directory.  To merge these changes into augur-contracts, there are scripts located in [the augur-contracts repository](https://github.com/AugurProject/augur-contracts). **In local deployments, this is not automatic.**

To merge the local changes into augur-contracts:

```bash
SOURCE="path/to/augur-core/output/contracts" BRANCH=master npm run update-contracts
```

Next, update the version of augur-contracts:
 - for _dev_ builds, increment the pre-release number
 - for _patches_, increment the patch number of the release build being patched; e.g., if 4.6.0 is the release, we are currently on 4.7.0-6, and we want to patch version 4.6, then we should use a patch to increment to 4.6.1
 - for _releases_, set the version to be the correct major/minor version; e.g., for dev build v4.7.0-10, the release version would be v4.7.0

```bash
npm version [<version>, major,minor,patch, prerelease]
git push && git push --tags
```

Finally, publish to NPM.  If this is a pre-release tag, deploy it to the `dev` channel.  The `dev` channel is the default for versions which are published from CI.

```bash
npm publish [--tag dev]
```

## Tests

The tests directory (augur-core/tests) contain tests and test fixtures to test the various functionalities present in Augur, including trading, reporting, and wcl tests.
- conftest.py -- contains the class ContractFixture, which deals with caching compiled contracts, signatures, etc. as well as resetting the blockchain before each test.
- delegation_sandbox.py -- tests the delegator contract.
- sandbox.py -- used for testing miscellaneous Solidity behaviors
- reporting -- contains tests for reporting purposes.
- trading -- contains tests for trading purposes.
- solidity_test_helpers -- small contracts to help run tests.
- test_controller.py -- tests controller functionalities.
- test_mutex.py -- tests mutex functionalities.
- test_helpers.py -- tests the controller, safeMath, and assertNoValue macros.
- test_legacyRep.py -- tests for legacyRepToken's functionalities.
- utils.py -- contains useful functions for testing, such as conversion between different data types.
- wcl-in-python.py -- contains functions for making and taking various types of bids.
- wcl.txt -- explains tests for the various situations when filling a bid and filling an ask.

Use pytest to run Augur's test suite:

```bash
pytest tests
```

This executes all the tests. To run a test individually, run the following:

```bash
pytest path/to/test_file.py -k 'name_of_test'
```

When writing tests, it is highly recommended to make use of the ContractFixtures class for "placeholder" variables. Python's unit testing framework comes handy here; encapsulate tests within functions that start with "test\_", and use `assert` statements when testing for certain values. Parameterized tests are recommended as well to test various possibilities and edge cases.

## Docker

augur-core can optionally be built, run, and tested using Docker.  A number of Docker commands are included as npm scripts, which map to the non-Dockerized versions where this makes sense. Docker commands beginning with `docker:run` execute the command within the Docker image. Docker commands without `run` (e.g. `docker:test`) first build the image, then execute `docker:run:<command>`.

### Build

```bash
npm run docker:build
```

### Test

```bash
# With a pre-built image
npm run docker:run:test:unit:all

# Build and run all unit tests and integration tests
npm run docker:test

# Build and run just integration test
npm run docker:test:integration
```

## Source code organization

Augur's smart contracts are organized into four folders:
- `source/contracts/factories`: Constructors for universes, markets, fee windows, etc.
- `source/contracts/libraries`: Data structures used elsewhere in the source code.
- `source/contracts/reporting`: Creation and manipulation of universes, markets, fee windows, and reporting-related tokens.
- `source/contracts/trading`: Functions to create, view, and fill orders, to issue and close out complete sets of shares, and for traders to claim proceeds after markets are closed.

## Additional notes

### General information about Augur

- [A Roadmap For Augur and What's Next](https://medium.com/@AugurProject/a-roadmap-for-augur-and-whats-next-930fe6c7f75a)
- [Augur Master Plan](https://medium.com/@AugurProject/augur-master-plan-42dda65a3e3d)

### Terminology

[Augur Terminology](http://blog.augur.net/faq/all-terms/)

### EVM numbers are always integers

There are no floating-point numbers in the EVM, only integers.  Therefore, Ether and Reputation values in contracts are always represented in units of wei (i.e., indivisible units of 10^-18 Ether or 10^-18 Reputation).

### Reporting diagrams

- [Reporting flow diagram](https://pasteboard.co/1FcgIDWR2.png)
- [More in-depth diagram](https://www.websequencediagrams.com/files/render?link=kUm7MBHLoO87M3m2dXzE)
- [Market object graph](https://pasteboard.co/1WHGfXjB3.png)

### Worst-case-loss escrow for trades

- [Some notes on worst-case-loss/value-at-risk](https://github.com/AugurProject/augur-core/blob/master/tests/wcl.txt)
