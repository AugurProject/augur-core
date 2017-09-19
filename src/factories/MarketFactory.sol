pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/reporting/IReportingWindow.sol';
import 'ROOT/reporting/IMarket.sol';
import 'ROOT/trading/ICash.sol';
import 'ROOT/IController.sol';


contract MarketFactory {
    function createMarket(IController _controller, IReportingWindow _reportingWindow, uint256 _endTime, uint8 _numOutcomes, uint256 _marketDenominator, uint256 _feePerEthInWei, ICash _denominationToken, address _creator, address _automatedReporterAddress, bytes32 _topic) public payable returns (IMarket _market) {
        Delegator _delegator = new Delegator(_controller, "Market");
        _market = IMarket(_delegator);
        _market.initialize.value(msg.value)(_reportingWindow, _endTime, _numOutcomes, _marketDenominator, _feePerEthInWei, _denominationToken, _creator, _automatedReporterAddress, _topic);
        return _market;
    }
}
