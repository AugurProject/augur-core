pragma solidity ^0.4.17;

import 'libraries/CashAutoConverter.sol';
import 'trading/ICash.sol';


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
