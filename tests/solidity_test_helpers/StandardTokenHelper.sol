pragma solidity ^0.4.20;

import 'libraries/token/StandardToken.sol';


contract StandardTokenHelper is StandardToken {
    function faucet(uint256 _amount) public returns (bool) {
        balances[msg.sender] = balances[msg.sender].add(_amount);
        supply = supply.add(_amount);
        return true;
    }

    function onTokenTransfer(address _from, address _to, uint256 _value) internal returns (bool) {
        return true;
    }
}
