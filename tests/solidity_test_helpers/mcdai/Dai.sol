pragma solidity ^0.4.24;

import 'TEST/StandardTokenHelper.sol';


contract Dai is StandardTokenHelper {
    function burn(address _target, uint256 _amount) public returns (bool) {
        balances[_target] = balances[_target].sub(_amount);
        supply = supply.sub(_amount);
        return true;
    }

    function mint(address _target, uint256 _amount) internal returns (bool) {
        balances[_target] = balances[_target].add(_amount);
        supply = supply.add(_amount);
        return true;
    }
}
