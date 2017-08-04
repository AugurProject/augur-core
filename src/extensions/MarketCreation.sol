pragma solidity ^0.4.13;


// FIXME: Remove this stub once the contract is implemented in Solidity
contract Market {
    function stub();
}


// FIXME: Remove this stub once the contract is implemented in Solidity
contract ReportingWindow {
    function createNewMarket(int256 _endTime, int256 _numOutcomes, int256 _payoutDenominator, int256 _feePerEthInWei, address _denominationToken, address _sender, int256 _minDisplayPrice, int256 _maxDisplayPrice, address _automatedReporterAddress, int256 _topic) payable returns (Market);
}


// FIXME: Remove this stub once the contract is implemented in Solidity
contract Branch {
    function getReportingWindowByMarketEndTime(int256 _endTime, int256 _hasAutomatedReporter) returns (ReportingWindow);
}

contract MarketCreation {
    function createScalarMarket(Branch _branch, int256 _endTime, int256 _feePerEthInWei, address _denominationToken, int256 _minDisplayPrice, int256 _maxDisplayPrice, address _automatedReporterAddress, int256 _topic) payable public returns (Market _market) {
        ReportingWindow _reportingWindow = _branch.getReportingWindowByMarketEndTime(_endTime, _automatedReporterAddress != 0 ? 1 : 0);
        _market = _reportingWindow.createNewMarket.value(msg.value)(_endTime, 2, _maxDisplayPrice - _minDisplayPrice, _feePerEthInWei, _denominationToken, msg.sender, _minDisplayPrice, _maxDisplayPrice, _automatedReporterAddress, _topic);
        return _market;
    }

    function createCategoricalMarket(Branch _branch, int256 _endTime, int256 _numOutcomes, int256 _feePerEthInWei, address _denominationToken, address _automatedReporterAddress, int256 _topic) payable public returns (Market _market) {
        ReportingWindow _reportingWindow = _branch.getReportingWindowByMarketEndTime(_endTime, _automatedReporterAddress != 0 ? 1 : 0);
        _market = _reportingWindow.createNewMarket.value(msg.value)(_endTime, _numOutcomes, _numOutcomes, _feePerEthInWei, _denominationToken, msg.sender, 0, 10 ** 18, _automatedReporterAddress, _topic);
        return _market;
    }
}