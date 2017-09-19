pragma solidity ^0.4.13;

import 'ROOT/libraries/CashWrapper.sol';


contract CashWrapperHelper is CashWrapper {
    function toCashFunction() public convertToCash payable returns (bool) {
        return true;
    }

    function toETHFunction() public convertFromCash returns (bool) {
        return true;
    }

    function getETHBalance(address _address) public returns (uint256) {
        return _address.balance;
    }
}
