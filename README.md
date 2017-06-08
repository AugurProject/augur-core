augur-core
----------

[![Build Status](https://travis-ci.org/AugurProject/augur-core.svg)](https://travis-ci.org/AugurProject/augur-core)

### Ethereum contracts for a decentralized prediction market platform

Depends on Serpent and Pyethereum

# Installation

You should already have a system-wide installation of python, and it should be set to python-2.7.x.

Install the serpent smart contract programming language.<br>
This can be installed system-wide if available on your OS or distribution.<br>
However, it is recommended to install the dev version of serpent directly from github as your user in your home directory as follows:

Serpent Installation:
```
git clone https://github.com/ethereum/serpent.git
cd serpent
git checkout develop
sudo pip install -r requirements-dev.txt
sudo python setup.py install
```

Next set up pyethereum, which includes the tools used to test Ethereum smart contracts from python scripts.<br>
(again, can be done as your preferred user from your home directory)

Pyethereum Installation:
```
git clone https://github.com/ethereum/pyethereum.git
cd pyethereum
git checkout develop
sudo pip install -r requirements.txt
sudo make && sudo make install
sudo python setup.py install
```

To install the augur-core Ethereum contracts:<br>
(again, can be done as your preferred user from your home directory or wherever you'd like them installed)
```
git clone https://github.com/AugurProject/augur-core.git
cd augur-core
git checkout develop
sudo pip install -r requirements.txt
sudo python setup.py install
```

Now we can try running some tests to make sure our installation worked.

Run some tests:
```
cd augur-core/tests
python ./runtests.py
```


# Docker

You may run augur-core using docker as follows:

### Build:
```
docker image build --tag augur-core-tests --file Dockerfile-test .
```

### Run:
```
docker container rm -f augur-core-tests; docker container run --rm -it --name augur-core-tests augur-core-tests
```

### Debug:
```
docker container rm -f augur-core-tests; docker container run --rm -it --name augur-core-tests --entrypoint /bin/bash augur-core-tests
py.test -s tests/trading_tests.py
```


# Additional Notes:

There are no floats or strings in the serpent language.
In cases where strings are used, they are actually stored numerically as integers.

All augur-core contracts use fixedpoint (no floats).  So sub-ether values in serpent would be represented as integers whose value
is in wei (attoEthers or 10**-18 Ethers).

To give an example, 200\*base / 5 would be 40 in that base.  To multiply two fixed point numbers like 5 times 10 an example in 
base 10\*\*18 would be 5\*10\*\*18 \* 10\*10\*\*18 / 10\*\*18
[we divide by the base to keep it in base 10\*\*18].  For a division example, 18/10 would be 18\*10\*\*18 \* 10\*\*18 / (10\*10\*\*18).

Also note, Mist uses a different contract abi style than usual, to convert use the following regex \((.\*?)\) and replace with nothing [except don't do it for events].


