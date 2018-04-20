pragma solidity 0.4.20;

import 'trading/Trade.sol';


contract TestTrade is Trade {
    function getMinGasNeeded() internal returns (uint256) {
        return 5000000;
    }
}