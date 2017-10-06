pragma solidity ^0.4.17;

import 'libraries/token/StandardToken.sol';


contract StandardTokenHelper is StandardToken {
    function faucet(uint256 _amount) public returns (bool) {
        balances[msg.sender] = balances[msg.sender].add(_amount);
        supply = supply.add(_amount);
        return true;
    }
}
