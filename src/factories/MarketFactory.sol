pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/reporting/ReportingWindow.sol';
import 'ROOT/reporting/Interfaces.sol';
import 'ROOT/Controller.sol';


contract MarketFactory {
    function createMarket(Controller _controller, ReportingWindow _reportingWindow, uint256 _endTime, int256 _numOutcomes, int256 _payoutDenominator, int256 _feePerEthInWei, address _denominationToken, address _creator, int256 _minDisplayPrice, int256 _maxDisplayPrice, address _automatedReporterAddress, int256 _topic) payable returns (IMarket _market) {
        Delegator _delegator = new Delegator(_controller, "market");
        _market = IMarket(_delegator);
        _market.initialize.value(msg.value)(_reportingWindow, _endTime, _numOutcomes, _payoutDenominator, _feePerEthInWei, _denominationToken, _creator, _minDisplayPrice, _maxDisplayPrice, _automatedReporterAddress, _topic);
        return _market;
    }
}
