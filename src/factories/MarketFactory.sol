pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/reporting/ReportingWindow.sol';
import 'ROOT/reporting/Market.sol';
import 'ROOT/trading/Cash.sol';
import 'ROOT/Controller.sol';


contract MarketFactory {
    function createMarket(Controller _controller, ReportingWindow _reportingWindow, uint256 _endTime, uint8 _numOutcomes, uint256 _payoutDenominator, uint256 _feePerEthInWei, Cash _denominationToken, address _creator, int256 _minDisplayPrice, int256 _maxDisplayPrice, address _automatedReporterAddress, bytes32 _topic) public payable returns (Market _market) {
        Delegator _delegator = new Delegator(_controller, "Market");
        _market = Market(_delegator);
        _market.initialize.value(msg.value)(_reportingWindow, _endTime, _numOutcomes, _payoutDenominator, _feePerEthInWei, _denominationToken, _creator, _minDisplayPrice, _maxDisplayPrice, _automatedReporterAddress, _topic);
        return _market;
    }
}