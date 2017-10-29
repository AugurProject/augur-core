pragma solidity 0.4.17;


import 'legacy_reputation/BasicToken.sol';
import 'legacy_reputation/ERC20.sol';


contract MockToken is ERC20, BasicToken {

//    function callInternalTransfer(address _from, address _to, uint256 _value) internal returns (bool) {
//        return internalTransfer(_from, _to, _value);
//    }

    function mint(address _target, uint256 _amount) returns (bool) {
        balances[_target] = balances[_target].add(_amount);
        return true;
    }

    function emitTransferLogs(address _from, address _to, uint256 _value) internal returns (bool) {
        return true;
    }
}
