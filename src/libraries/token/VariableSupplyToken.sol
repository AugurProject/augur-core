pragma solidity ^0.4.13;

import 'ROOT/libraries/token/StandardToken.sol';


contract VariableSupplyToken is StandardToken {
    using SafeMathUint256 for uint256;

    event Mint(address indexed target, uint256 value);
    event Burn(address indexed target, uint256 value);

    function mint(address _target, uint256 _amount) internal returns (bool) {
        balances[_target] = balances[_target].add(_amount);
        totalSupply = totalSupply.add(_amount);
        Mint(_target, _amount);
        return true;
    }

    function burn(address _target, uint256 _amount) internal returns (bool) {
        balances[_target] = balances[_target].sub(_amount);
        totalSupply = totalSupply.sub(_amount);
        Burn(_target, _amount);
        return true;
    }
}
