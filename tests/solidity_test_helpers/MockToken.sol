pragma solidity 0.4.17;


import 'libraries/token/BasicToken.sol';


contract MockToken is BasicToken {

    function callInternalTransfer(address _from, address _to, uint256 _value) returns (bool) {
        return internalTransfer(_from, _to, _value);
    }

    function mint(address _target, uint256 _amount) returns (bool) {
        balances[_target] = balances[_target].add(_amount);
        return true;
    }
}
