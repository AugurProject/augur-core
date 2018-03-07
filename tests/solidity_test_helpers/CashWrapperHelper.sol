pragma solidity ^0.4.20;

import 'libraries/CashAutoConverter.sol';
import 'trading/ICash.sol';


contract CashWrapperHelper is CashAutoConverter {
    function toEthFunction() public convertToAndFromCash returns (bool) {
        return true;
    }
}
