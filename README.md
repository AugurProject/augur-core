augur-core
----------

[![Build Status](https://travis-ci.org/AugurProject/augur-core.svg)](https://travis-ci.org/AugurProject/augur-core)

Ethereum contracts for a decentralized prediction market platform

Note: all augur-core contracts use fixedpoint.  To give an example, 200\*base / 5 would be 40 in that base.
To multiply two fixed point numbers like 5 times 10 an example in base 10\*\*18 would be 5\*10\*\*18 \* 10\*10\*\*18 / 10\*\*18
[we divide by the base to keep it in base 10\*\*18].  For a division example, 18/10 would be 18\*10\*\*18 \* 10\*\*18 / (10\*10\*\*18).

Also note, Mist uses a different contract abi style than usual, to convert use the following regex \((.\*?)\) and replace with nothing [except don't do it for events].

Depends on Serpent and Pyethereum