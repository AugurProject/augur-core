pragma solidity ^0.4.13;

import 'ROOT/libraries/CashAutoConverter.sol';
import 'ROOT/trading/ICash.sol';


contract CashWrapperHelper is CashAutoConverter {
    function toCashFunction(uint256 _balance) public convertToAndFromCash payable returns (bool) {
        ICash _cash = ICash(controller.lookup("Cash"));
        require(_cash.balanceOf(msg.sender) == _balance);
        return true;
    }

    function toETHFunction() public convertToAndFromCash returns (bool) {
        return true;
    }
}
