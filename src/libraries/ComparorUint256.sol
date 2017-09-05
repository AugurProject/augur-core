pragma solidity ^0.4.13;
import "ROOT/libraries/DelegationTarget.sol";


contract ComparorUint256 is DelegationTarget {

    function compare(uint256 _firstItem, uint256 _secondItem) public constant returns (int256) {
        if (_firstItem < _secondItem) {
            return (-1);
        } else if (_firstItem > _secondItem) {
            return (1);
        }
        return (0);
    }

}
