augur-core
----------

[![Build Status](https://travis-ci.org/AugurProject/augur-core.svg)](https://travis-ci.org/AugurProject/augur-core)

### Ethereum contracts for a decentralized prediction market platform

Depends on Serpent and Pyethereum

# Installation

You should already have a system-wide installation of python, and it should be set to python-2.7.x.

First set up pyethereum, which includes the tools used to test Ethereum smart contracts from python scripts, and the serpent smart contract programming language. <br>
(can be done as your preferred user from your home directory)

Pyethereum & Serpent Installation:
```
sudo pip install -r requirements.txt
```


Serpent can also be installed system-wide if available on your OS or distribution so you can do things like serpent compile and serpent mk_full_signature.<br>
It is recommended to install the dev version of serpent directly from github as your user in your home directory as follows:

Serpent Installation:
```
git clone https://github.com/ethereum/serpent.git
cd serpent
git checkout develop
sudo pip install pytest
sudo make && sudo make install
sudo python setup.py install
```

Now we can try running some tests to make sure our installation worked.

Run some tests:
```
cd tests
python runtests.py
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

There are no floats in the serpent language.
In cases where strings are used, they are actually stored numerically as integers.

All augur-core contracts use fixedpoint (no floats).  So sub-ether values in serpent would be represented as integers whose value
is in wei (attoEthers or 10**-18 Ethers).

To give an example, 200\*base / 5 would be 40 in that base.  To multiply two fixed point numbers like 5 times 10 an example in 
base 10\*\*18 would be 5\*10\*\*18 \* 10\*10\*\*18 / 10\*\*18
[we divide by the base to keep it in base 10\*\*18].  For a division example, 18/10 would be 18\*10\*\*18 \* 10\*\*18 / (10\*10\*\*18).

Also note, Mist uses a different contract abi style than usual, to convert use the following regex \((.\*?)\) and replace with nothing [except don't do it for events].

# Resources to learn about serpent

https://github.com/ethereum/wiki/wiki/Serpent

https://www.cs.umd.edu/~elaine/smartcontract/guide.pdf

# More on Augur / high level

https://medium.com/@AugurProject/a-roadmap-for-augur-and-whats-next-930fe6c7f75a

https://medium.com/@AugurProject/augur-master-plan-42dda65a3e3d

# New reporting system info

[Flow diagram](https://pasteboard.co/1FcgIDWR2.png)

[More in depth diagram](https://www.websequencediagrams.com/files/render?link=kUm7MBHLoO87M3m2dXzE)

[Market object graph](https://pasteboard.co/1WHGfXjB3.png)

# Trading wcl info

More on worst case loss / value at risk: https://github.com/AugurProject/augur-core/blob/develop/tests/wcl.txt
