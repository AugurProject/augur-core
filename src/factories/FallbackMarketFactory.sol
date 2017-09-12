pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/reporting/IReportingWindow.sol';
import 'ROOT/reporting/IMarket.sol';
import 'ROOT/trading/ICash.sol';
import 'ROOT/IController.sol';


contract FallbackMarketFactory {
    function createMarket(IController _controller, IReportingWindow _reportingWindow) public returns (IMarket _market) {
        Delegator _delegator = new Delegator(_controller, "FallbackMarket");
        _market = IMarket(_delegator);
        _market.initialize(_reportingWindow, 0, 0, 0, 0, ICash(0), 0, 0, 0, 0, 0);
        return _market;
    }
}
