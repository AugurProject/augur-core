augur-core
----------

[![Build Status](https://travis-ci.org/AugurProject/augur-core.svg)](https://travis-ci.org/AugurProject/augur-core)

Ethereum contracts for a decentralized prediction market platform

Note: all augur-core contracts use fixedpoint.  To give an example, 200*base / 5 would be 40 in that base.
To multiply two fixed point numbers like 5 times 10 an example in base 10**20 would be 5*10**20 * 10*10**20 / 10**20
[we divide by the base to keep it in base 10**20].  For a division example, 20/10 would be 20*10**20 * 10**20 / (10*10**20).

Also note, Mist uses a different contract abi style than usual, to convert use the following regex \((.*?)\) and replace with nothing.