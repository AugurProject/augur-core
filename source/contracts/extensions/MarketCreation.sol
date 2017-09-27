pragma solidity ^0.4.13;

import 'reporting/IBranch.sol';
import 'reporting/IMarket.sol';
import 'trading/ICash.sol';
import 'reporting/IReportingWindow.sol';


contract MarketCreation {
    function createMarket(IBranch _branch, uint256 _endTime, uint8 _numOutcomes, uint256 _feePerEthInWei, ICash _denominationToken, uint256 _numTicks, address _automatedReporterAddress) payable public returns (IMarket) {
        IReportingWindow _reportingWindow = _branch.getReportingWindowByMarketEndTime(_endTime, (_automatedReporterAddress != 0));
        return _reportingWindow.createNewMarket.value(msg.value)(_endTime, _numOutcomes, _numTicks, _feePerEthInWei, _denominationToken, msg.sender, _automatedReporterAddress);
    }
}
