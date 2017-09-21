pragma solidity ^0.4.13;

import 'ROOT/libraries/CashWrapper.sol';
import 'ROOT/trading/ICash.sol';


contract CashWrapperHelper is CashWrapper {
    function toCashFunction(uint256 _balance) public convertToCash payable returns (bool) {
        ICash _cash = ICash(controller.lookup("Cash"));
        require(_cash.balanceOf(msg.sender) == _balance);
        return true;
    }

    function toETHFunction() public convertFromCash returns (bool) {
        return true;
    }
}
