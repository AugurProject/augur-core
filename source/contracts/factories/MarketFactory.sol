pragma solidity 0.4.17;


import 'libraries/Delegator.sol';
import 'reporting/IReportingWindow.sol';
import 'reporting/IMarket.sol';
import 'trading/ICash.sol';
import 'IController.sol';


contract MarketFactory {
    function createMarket(IController _controller, IReportingWindow _reportingWindow, uint256 _endTime, uint8 _numOutcomes, uint256 _numTicks, uint256 _feePerEthInWei, ICash _denominationToken, address _creator, address _designatedReporterAddress) public payable returns (IMarket _market) {
        Delegator _delegator = new Delegator(_controller, "Market");
        _market = IMarket(_delegator);
        _market.initialize.value(msg.value)(_reportingWindow, _endTime, _numOutcomes, _numTicks, _feePerEthInWei, _denominationToken, _creator, _designatedReporterAddress);
        return _market;
    }
}
