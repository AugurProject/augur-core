pragma solidity 0.4.17;


import 'libraries/Delegator.sol';
import 'reporting/IReportingWindow.sol';
import 'reporting/IMarket.sol';
import 'trading/ICash.sol';
import 'IController.sol';


contract MarketFactory {
    function createMarket(IController _controller) public returns (IMarket _market) {
        Delegator _delegator = new Delegator(_controller, "Market");
        _market = IMarket(_delegator);
        return _market;
    }
}
