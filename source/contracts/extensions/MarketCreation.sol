pragma solidity ^0.4.17;

import 'reporting/IUniverse.sol';
import 'reporting/IMarket.sol';
import 'trading/ICash.sol';
import 'reporting/IReportingWindow.sol';


contract MarketCreation {
    function createMarket(IUniverse _universe, uint256 _endTime, uint8 _numOutcomes, uint256 _feePerEthInWei, ICash _denominationToken, uint256 _numTicks, address _designatedReporterAddress) payable public returns (IMarket) {
        IReportingWindow _reportingWindow = _universe.getReportingWindowByMarketEndTime(_endTime, (_designatedReporterAddress != 0));
        return _reportingWindow.createNewMarket.value(msg.value)(_endTime, _numOutcomes, _numTicks, _feePerEthInWei, _denominationToken, msg.sender, _designatedReporterAddress);
    }
}
