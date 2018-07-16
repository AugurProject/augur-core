pragma solidity 0.4.20;

import 'trading/Trade2.sol';


contract TestTrade is Trade2 {
    function getFillOrderMinGasNeeded() internal pure returns (uint256) {
        return 5000000;
    }
    function getCreateOrderMinGasNeeded() internal pure returns (uint256) {
        return 5000000;
    }
}
