pragma solidity ^0.4.13;

import 'ROOT/reporting/Interfaces.sol';
import 'ROOT/reporting/Branch.sol';
import 'ROOT/reporting/Market.sol';
import 'ROOT/trading/Cash.sol';
import 'ROOT/reporting/ReportingWindow.sol';


contract MarketCreation {
    function createScalarMarket(Branch _branch, uint256 _endTime, uint256 _feePerEthInWei, Cash _denominationToken, int256 _minDisplayPrice, int256 _maxDisplayPrice, address _automatedReporterAddress, bytes32 _topic) payable public returns (Market) {
        ReportingWindow _reportingWindow = _branch.getReportingWindowByMarketEndTime(_endTime, (_automatedReporterAddress != 0));
        return _reportingWindow.createNewMarket.value(msg.value)(_endTime, 2, uint256(_maxDisplayPrice - _minDisplayPrice), _feePerEthInWei, _denominationToken, msg.sender, _minDisplayPrice, _maxDisplayPrice, _automatedReporterAddress, _topic);
    }

    function createCategoricalMarket(Branch _branch, uint256 _endTime, uint8 _numOutcomes, uint256 _feePerEthInWei, Cash _denominationToken, address _automatedReporterAddress, bytes32 _topic) payable public returns (Market) {
        ReportingWindow _reportingWindow = _branch.getReportingWindowByMarketEndTime(_endTime, (_automatedReporterAddress != 0));
        return _reportingWindow.createNewMarket.value(msg.value)(_endTime, _numOutcomes, _numOutcomes, _feePerEthInWei, _denominationToken, msg.sender, 0, 10 ** 18, _automatedReporterAddress, _topic);
    }
}
