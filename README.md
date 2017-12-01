# augur-core

[![Build Status](https://travis-ci.org/AugurProject/augur-core.svg)](https://travis-ci.org/AugurProject/augur-core)

Smart contracts for [Augur](https://augur.net), a decentralized prediction market platform on the [Ethereum](https://ethereum.org) blockchain.

## Installation

You need a system-wide installation of Python (v2.7.6 or higher).  Install the dependencies:

```bash
npm install npx
npm install
pip install -r requirements.txt
```

The dependencies include [pyethereum](https://github.com/ethereum/pyethereum), which is used to unit test our Ethereum smart contracts.  If you want to run the the augur-node tests locally, you also need to install [version 0.4.18 of the Solidity compiler](https://github.com/ethereum/solidity/releases/tag/v0.4.18) (`solc`) on your machine for pyethereum to run correctly.  (On macOS, you need to use [virtualenv](https://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/) or [homebrew](https://brew.sh/) Python to work around System Integrity Protection.)

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

All deployment commands can be managed through scripts in package.json, and are accessible to `npm run` and `yarn`.

### Manual Rinkeby deployment

Build and create compile artifacts:

```bash
augur-core % npm run build
```

Deploy to Rinkeby:

```bash
augur-core % RINKEBY_PRIVATE_KEY=$(cat path/to/keys/deploy_keys/rinkeby.prv) npm run deploy:rinkeby
```

### Updating augur-contracts

Manual deployment generates artifacts in the `output/contracts` directory.  To merge these changes into augur-contracts, there are scripts located in [the augur-contracts repository](https://github.com/AugurProject/augur-contracts). **In local deployments, this is not automatic.**

To merge the local changes into the augur-contracts repository:

```bash
augur-contracts % SOURCE="path/to/augur-core/output/contracts" BRANCH=master npm run update-contracts
```

Next, update the version of augur-contracts:
 - for _dev_ builds, increment the pre-release number
 - for _patches_, increment the patch number of the release build being patched; e.g., if 4.6.0 is the release, we are currently on 4.7.0-6, and we want to patch version 4.6, then we should use a patch to increment to 4.6.1
 - for _releases_, set the version to be the correct major/minor version; e.g., for dev build v4.7.0-10, the release version would be v4.7.0

```bash
augur-contracts % npm version [<version>, major,minor,patch, prerelease]
augur-contracts % git push && git push --tags
```

Finally, publish to NPM.  If this is a pre-release tag, deploy it to the `dev` channel.  The `dev` channel is the default for versions which are published from CI.

```bash
augur-contracts % npm publish [--tag dev]
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
- test_legacyRep.py -- tests the legacyRepTokens' functionalities.
- utils.py -- contains useful functions for testing, such as conversion between different data types.
- wcl-in-python.py -- contains functions for making and taking various types of bids.
- wcl.txt -- explains tests for the various situations when filling a bid and filling an ask.

In order to run Augur's test suite, run the following inside the tests directory:

```bash
cd augur-core/tests
pytest
```

This executes all the tests. To run a test individually, run the following:

```bash
pytest path/to/test_file.py -k 'name_of_test'
```

The unit test suite includes tests that use a fuzzer, which take somewhat longer (around 10 minutes on CI) to run than the rest of the tests.  These tests are _not_ run by default; to include these tests, set the environment variable `INCLUDE_FUZZY_TESTS=1`:

```bash
INCLUDE_FUZZY_TESTS=1 pytest trading/test_wcl_fuzzy.py
```

Or if you want to run all tests (including fuzzy):

```bash
INCLUDE_FUZZY_TESTS=1 pytest
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
- `source/contracts/factories`: Constructors for universes, markets, reporting windows, etc.
- `source/contracts/libraries`: Data structures used elsewhere in the source code.
- `source/contracts/reporting`: Creation and manipulation of universes, markets, reporting windows, and reporting-related tokens.
- `source/contracts/trading`: Functions to create, view, and fill orders, to issue and close out complete sets of shares, and for traders to claim proceeds after markets are closed.

## Additional notes

### General information about Augur

- [A Roadmap For Augur and What's Next](https://medium.com/@AugurProject/a-roadmap-for-augur-and-whats-next-930fe6c7f75a)
- [Augur Master Plan](https://medium.com/@AugurProject/augur-master-plan-42dda65a3e3d)

### Terminology

[Augur Terminology](http://blog.augur.net/faq/all-terms/)

### Security model

The security model is based on the idea that reporters will want to invest in a market where honesty prevails, and will not trust fraudulent markets. For example, assume that there exist two almost identical universes: an honest universe, where the factually correct answer is the predominant answer, and a fraudulent universe, where incorrect answers are predominant in order to cheat the system. The REP in the fraudulent universe will approach 0, and the REP in the honest universe will approach the theoretical yield. This phenomenon occurs because reporters do not want to trade on markets in a dishonest universe. Therefore, they will not create markets in a dishonest universe, and the REP holders will not receive any market fees.

In order to create a fraudulent universe, an attacker must fork the main universe. They will need to buy a large share of REP and stake it on the lie outcome, as nobody else will want to engage in a deceitful market. In principle, the attacker will lose up to 2.5 times the maximum profit made from a successful attack, and their REP will approach 0.

The reentrancy guard (libraries/ReentrancyGuard.sol) and controller (Controller.sol) contracts also help uphold security. One can also attack Ethereum contracts by creating a chain of wanted contract calls through a malicious user. The reentrancy guard protects against that by preventing someone from re-entering the contracts before they return. The controller contract serves to update Augur and stores a registry of whitelisted contract addresses. The controller also can perform administrative actions, such as transferring ownership and performing emergency stop functions. It can be operated in either the developer mode, where the developer updates contracts, or the decentralized mode, when people must upload contracts to make changes and therefore, the market creators/traders must cancel orders and shift to the new contract. For bugs found involving money or REP, contracts are locked / an escape hatch is enabled which allows withdrawal of shares (and cancelling orders) for a value half-way between the bid-ask spread at the time of the lock. In addition, another escape hatch is enabled, which allows withdrawal of any locked up REP.

### EVM numbers are always integers

There are no floating point numbers in the EVM. All augur-core contracts use integers. So ether values in contracts will always be represented in units of wei (AKA attoether AKA 10^-18 ether).

### Reporting diagrams

- [Reporting flow diagram](https://pasteboard.co/1FcgIDWR2.png)
- [More in-depth diagram](https://www.websequencediagrams.com/files/render?link=kUm7MBHLoO87M3m2dXzE)
- [Market object graph](https://pasteboard.co/1WHGfXjB3.png)

### Worst-case-loss escrow for trades

- [Some notes on worst-case-loss/value-at-risk](https://github.com/AugurProject/augur-core/blob/master/tests/wcl.txt)
