# augur-core

[![Build Status](https://travis-ci.org/AugurProject/augur-core.svg)](https://travis-ci.org/AugurProject/augur-core)

Ethereum contracts for a decentralized prediction market platform.

## Installation

You should already have a system-wide installation of Python and it should be
Python 2.7.

First install the dependencies, which include PyEthereum (the tool used to test
Ethereum smart contracts from Python scripts) and the Serpent smart contract
programming language:

```
sudo pip install -r requirements.txt
```

(If installed outside of a Python virtualenv Serpent will be installed to
`./src/serpent`. This isn't ideal but won't hurt anything.)

Now we can try running some tests to make sure our installation worked:

```
cd tests
python runtests.py
```

## Docker

You may run augur-core using docker as follows:

### Build:

```
docker image build --tag augur-core-tests --file Dockerfile-test .
```

### Run:

```
docker container rm -f augur-core-tests
docker container run --rm -it --name augur-core-tests augur-core-tests
```

### Debug:

```
docker container rm -f augur-core-tests
docker container run --rm -it --name augur-core-tests --entrypoint /bin/bash augur-core-tests
py.test -s tests/trading_tests.py
```

## Additional notes

There are no floats in Serpent.

Strings are stored numerically as integers.

All augur-core contracts use fixedpoint (no floats). So sub-ether values in
Serpent would be represented as integers whose value is in wei (attoEthers or
10**-18 Ethers).

To give an example, 200\*base / 5 would be 40 in that base.

To multiply two
fixed point numbers like 5 times 10 an example in base 10\*\*18 would be
5\*10\*\*18 \* 10\*10\*\*18 / 10\*\*18 (we divide by the base to keep it in
base 10\*\*18).

For a division example, 18/10 would be 18\*10\*\*18 \* 10\*\*18 /
(10\*10\*\*18).

Also note, Mist uses a different contract abi style than usual, to convert use
the regex `((.*?))` and replace with nothing (except don't do it for
events).

## General information about Serpent

- [The Serpent wiki](https://github.com/ethereum/wiki/wiki/Serpent)
- [The Serpent guide](https://www.cs.umd.edu/~elaine/smartcontract/guide.pdf) (PDF)

## General information about Augur

- [A Roadmap For Augur and What’s Next](https://medium.com/@AugurProject/a-roadmap-for-augur-and-whats-next-930fe6c7f75a)
- [Augur Master Plan](https://medium.com/@AugurProject/augur-master-plan-42dda65a3e3d)

## Information about the new reporting system

- [Flow diagram](https://pasteboard.co/1FcgIDWR2.png)
- [More in depth diagram](https://www.websequencediagrams.com/files/render?link=kUm7MBHLoO87M3m2dXzE)
- [Market object graph](https://pasteboard.co/1WHGfXjB3.png)

## Information about trading worst case loss (WCL)

- [Some notes on WCL/value at risk](https://github.com/AugurProject/augur-core/blob/develop/tests/wcl.txt)
