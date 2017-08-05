pragma solidity ^0.4.13;


import 'ROOT/reporting/Interfaces.sol';


contract MarketCreation {
    function createScalarMarket(IBranch _branch, int256 _endTime, int256 _feePerEthInWei, address _denominationToken, int256 _minDisplayPrice, int256 _maxDisplayPrice, address _automatedReporterAddress, int256 _topic) payable public returns (IMarket) {
        IReportingWindow _reportingWindow = _branch.getReportingWindowByMarketEndTime(_endTime, (_automatedReporterAddress != 0) ? 1 : 0);
        return _reportingWindow.createNewMarket.value(msg.value)(_endTime, 2, _maxDisplayPrice - _minDisplayPrice, _feePerEthInWei, _denominationToken, msg.sender, _minDisplayPrice, _maxDisplayPrice, _automatedReporterAddress, _topic);
    }

    function createCategoricalMarket(IBranch _branch, int256 _endTime, int256 _numOutcomes, int256 _feePerEthInWei, address _denominationToken, address _automatedReporterAddress, int256 _topic) payable public returns (IMarket) {
        IReportingWindow _reportingWindow = _branch.getReportingWindowByMarketEndTime(_endTime, (_automatedReporterAddress != 0) ? 1 : 0);
        return _reportingWindow.createNewMarket.value(msg.value)(_endTime, _numOutcomes, _numOutcomes, _feePerEthInWei, _denominationToken, msg.sender, 0, 10 ** 18, _automatedReporterAddress, _topic);
    }
}