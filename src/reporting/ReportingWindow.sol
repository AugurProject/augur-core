// Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE

pragma solidity ^0.4.13;

import 'ROOT/reporting/IReportingWindow.sol';
import 'ROOT/libraries/DelegationTarget.sol';
import 'ROOT/libraries/Typed.sol';
import 'ROOT/libraries/Initializable.sol';
import 'ROOT/reporting/IBranch.sol';
import 'ROOT/reporting/IReputationToken.sol';
import 'ROOT/reporting/IRegistrationToken.sol';
import 'ROOT/reporting/IMarket.sol';
import 'ROOT/reporting/IReportingToken.sol';
import 'ROOT/trading/ICash.sol';
import 'ROOT/factories/MarketFactory.sol';
import 'ROOT/factories/SetFactory.sol';
import 'ROOT/factories/RegistrationTokenFactory.sol';
import 'ROOT/reporting/Reporting.sol';


contract ReportingWindow is DelegationTarget, Typed, Initializable, IReportingWindow {
    IBranch private branch;
    uint256 private startTime;
    IRegistrationToken private registrationToken;
    Set private markets;
    Set private limitedReporterMarkets;
    Set private allReporterMarkets;
    mapping(address => Set) private reportsByReporter;
    mapping(address => uint256) private numberOfReportsByMarket;
    uint256 private constant BASE_MINIMUM_REPORTERS_PER_MARKET = 7;

    function initialize(IBranch _branch, uint256 _reportingWindowId) public beforeInitialized returns (bool) {
        endInitialization();
        branch = _branch;
        startTime = _reportingWindowId * branch.getReportingPeriodDurationInSeconds();
        RegistrationTokenFactory _registrationTokenFactory = RegistrationTokenFactory(controller.lookup("RegistrationTokenFactory"));
        registrationToken = _registrationTokenFactory.createRegistrationToken(controller, this);
        SetFactory _setFactory = SetFactory(controller.lookup("SetFactory"));
        markets = _setFactory.createSet(controller, this);
        limitedReporterMarkets = _setFactory.createSet(controller, this);
        allReporterMarkets = _setFactory.createSet(controller, this);
        return true;
    }

    function createNewMarket(uint256 _endTime, uint8 _numOutcomes, uint256 _payoutDenominator, uint256 _feePerEthInWei, ICash _denominationToken, address _creator, int256 _minDisplayPrice, int256 _maxDisplayPrice, address _automatedReporterAddress, bytes32 _topic) public afterInitialized payable returns (IMarket _newMarket) {
        require(2 <= _numOutcomes && _numOutcomes <= 8);
        require(2 <= _payoutDenominator && _payoutDenominator <= 2**254);
        require(block.timestamp < startTime);
        require(branch.getReportingWindowByMarketEndTime(_endTime, _automatedReporterAddress != 0).getTypeName() == "ReportingWindow");
        _newMarket = MarketFactory(controller.lookup("MarketFactory")).createMarket.value(msg.value)(controller, this, _endTime, _numOutcomes, _payoutDenominator, _feePerEthInWei, _denominationToken, _creator, _minDisplayPrice, _maxDisplayPrice, _automatedReporterAddress, _topic);
        markets.addSetItem(_newMarket);
        limitedReporterMarkets.addSetItem(_newMarket);
        return _newMarket;
    }

    function migrateMarketInFromSibling() public afterInitialized returns (bool) {
        IMarket _market = IMarket(msg.sender);
        IReportingWindow _shadyReportingWindow = _market.getReportingWindow();
        require(branch.isContainerForReportingWindow(_shadyReportingWindow));
        IReportingWindow _originalReportingWindow = _shadyReportingWindow;
        require(_originalReportingWindow.isContainerForMarket(_market));
        privateAddMarket(_market);
        return true;
    }

    function migrateMarketInFromNibling() public afterInitialized returns (bool) {
        IMarket _market = IMarket(msg.sender);
        IBranch _shadyBranch = _market.getBranch();
        require(_shadyBranch == branch.getParentBranch());
        IBranch _originalBranch = _shadyBranch;
        IReportingWindow _shadyReportingWindow = _market.getReportingWindow();
        require(_originalBranch.isContainerForReportingWindow(_shadyReportingWindow));
        IReportingWindow _originalReportingWindow = _shadyReportingWindow;
        require(_originalReportingWindow.isContainerForMarket(_market));
        privateAddMarket(_market);
        return true;
    }

    function removeMarket() public afterInitialized returns (bool) {
        IMarket _market = IMarket(msg.sender);
        require(markets.contains(_market));
        markets.remove(_market);
        limitedReporterMarkets.remove(_market);
        allReporterMarkets.remove(_market);
        return true;
    }

    function updateMarketPhase() public afterInitialized returns (bool) {
        IMarket _market = IMarket(msg.sender);
        require(markets.contains(_market));
        IMarket.ReportingState _state = _market.getReportingState();
        if (_state > IMarket.ReportingState.ALL_REPORTING) {
            allReporterMarkets.remove(_market);
            limitedReporterMarkets.remove(_market);
            return false;
        }
        if (_state > IMarket.ReportingState.LIMITED_REPORTING) {
            allReporterMarkets.addSetItem(_market);
            limitedReporterMarkets.remove(_market);
            return false;
        }
        // defaults to in limited reporter markets
        allReporterMarkets.remove(_market);
        limitedReporterMarkets.addSetItem(_market);
        return true;
    }

    function noteReport(IMarket _market, address _reporter, bytes32 _payoutDistributionHash) public afterInitialized returns (bool) {
        require(markets.contains(_market));
        require(_market.getReportingTokenOrZeroByPayoutDistributionHash(_payoutDistributionHash) == msg.sender);
        IMarket.ReportingState _state = _market.getReportingState();
        require(_state == IMarket.ReportingState.ALL_REPORTING || _state == IMarket.ReportingState.LIMITED_REPORTING);

        if (_state == IMarket.ReportingState.ALL_REPORTING) {
            // always give credit for events in all-reporters phase
            privateNoteReport(_market, _reporter);
        } else if (numberOfReportsByMarket[_market] < getMaxReportsPerLimitedReporterMarket()) {
            // only give credit for limited reporter markets up to the max reporters for that market
            privateNoteReport(_market, _reporter);
        }
        // no credit in all other cases (but user can still report)
        return true;
    }

    function getTypeName() public afterInitialized constant returns (bytes32) {
        return "ReportingWindow";
    }

    function getBranch() public afterInitialized constant returns (IBranch) {
        return branch;
    }

    function getRegistrationToken() public afterInitialized constant returns (IRegistrationToken) {
        return registrationToken;
    }

    function getReputationToken() public afterInitialized constant returns (IReputationToken) {
        return branch.getReputationToken();
    }

    function getStartTime() public afterInitialized constant returns (uint256) {
        return startTime;
    }

    function getEndTime() public afterInitialized constant returns (uint256) {
        return getDisputeEndTime();
    }

    function getReportingStartTime() public afterInitialized constant returns (uint256) {
        return getStartTime();
    }

    function getReportingEndTime() public afterInitialized constant returns (uint256) {
        return getStartTime() + Reporting.reportingDurationSeconds();
    }

    function getDisputeStartTime() public afterInitialized constant returns (uint256) {
        return getReportingEndTime();
    }

    function getDisputeEndTime() public afterInitialized constant returns (uint256) {
        return getDisputeStartTime() + Reporting.reportingDisputeDurationSeconds();
    }

    function isActive() public afterInitialized constant returns (bool) {
        if (block.timestamp <= getStartTime()) {
            return false;
        }
        if (block.timestamp >= getEndTime()) {
            return false;
        }
        return true;
    }

    function isReportingActive() public afterInitialized constant returns (bool) {
        if (block.timestamp <= getStartTime()) {
            return false;
        }
        if (block.timestamp >= getReportingEndTime()) {
            return false;
        }
        return true;
    }

    function isDisputeActive() public afterInitialized constant returns (bool) {
        if (block.timestamp <= getDisputeStartTime()) {
            return false;
        }
        if (block.timestamp >= getEndTime()) {
            return false;
        }
        return true;
    }

    function getTargetReportsPerLimitedReporterMarket() public afterInitialized constant returns (uint256) {
        uint256 _limitedReporterMarketCount = limitedReporterMarkets.count();
        uint256 _registeredReporters = registrationToken.getPeakSupply();
        uint256 _minimumReportsPerMarket = BASE_MINIMUM_REPORTERS_PER_MARKET;
        uint256 _totalReportsForAllLimitedReporterMarkets = _minimumReportsPerMarket * _limitedReporterMarketCount;

        if (_registeredReporters > _totalReportsForAllLimitedReporterMarkets) {
            uint256 _factor = _registeredReporters / _totalReportsForAllLimitedReporterMarkets;
            _minimumReportsPerMarket = _minimumReportsPerMarket * _factor;
        }

        return _minimumReportsPerMarket;
    }

    function getNumberOfReportsByMarket(IMarket _market) public afterInitialized constant returns (uint256) {
        return numberOfReportsByMarket[_market];
    }

    function getMaxReportsPerLimitedReporterMarket() public afterInitialized constant returns (uint256) {
        return getTargetReportsPerLimitedReporterMarket() + 2;
    }

    function getRequiredReportsPerReporterForlimitedReporterMarkets() public afterInitialized constant returns (uint256) {
        return getTargetReportsPerLimitedReporterMarket() * limitedReporterMarkets.count() / registrationToken.totalSupply();
    }

    function getTargetReportsPerReporter() public afterInitialized constant returns (uint256) {
        uint256 _limitedMarketReportsPerReporter = getRequiredReportsPerReporterForlimitedReporterMarkets();
        return allReporterMarkets.count() + _limitedMarketReportsPerReporter;
    }

    function getLimitedReporterMarkets() public afterInitialized constant returns (Set) {
        return limitedReporterMarkets;
    }

    function getMarketsCount() public afterInitialized constant returns (uint256) {
        return markets.count();
    }

    function getLimitedReporterMarketsCount() public afterInitialized constant returns (uint256) {
        return limitedReporterMarkets.count();
    }

    function getAllReporterMarketsCount() public afterInitialized constant returns (uint256) {
        return allReporterMarkets.count();
    }

    function getReportsByReporter(address _reporter) public afterInitialized constant returns (Set) {
        if (reportsByReporter[_reporter] == address(0)) {
            reportsByReporter[_reporter] = SetFactory(controller.lookup("SetFactory")).createSet(controller, this);
        }
        return reportsByReporter[_reporter];
    }

    function isContainerForRegistrationToken(IRegistrationToken _shadyRegistrationToken) public afterInitialized constant returns (bool) {
        if (_shadyRegistrationToken.getTypeName() != "RegistrationToken") {
            return false;
        }
        return registrationToken == _shadyRegistrationToken;
    }

    function isContainerForMarket(IMarket _shadyMarket) public afterInitialized constant returns (bool) {
        if (_shadyMarket.getTypeName() != "Market") {
            return false;
        }
        return markets.contains(_shadyMarket);
    }

    function isDoneReporting(address _reporter) public afterInitialized constant returns (bool) {
        return getReportsByReporter(_reporter).count() >= getTargetReportsPerReporter();
    }

    function privateAddMarket(IMarket _market) private afterInitialized returns (bool) {
        require(!markets.contains(_market));
        require(!limitedReporterMarkets.contains(_market));
        require(!allReporterMarkets.contains(_market));
        markets.addSetItem(_market);
        IMarket.ReportingState _state = _market.getReportingState();
        if (_state > IMarket.ReportingState.ALL_REPORTING) {
            return false;
        }
        if (_state > IMarket.ReportingState.LIMITED_REPORTING) {
            allReporterMarkets.addSetItem(_market);
            return true;
        }
        limitedReporterMarkets.addSetItem(_market);
        return true;
    }

    function privateNoteReport(IMarket _market, address _reporter) private afterInitialized returns (bool) {
        Set reports = getReportsByReporter(_reporter);
        if (reports.contains(_market)) {
            return true;
        }
        reports.addSetItem(_market);
        numberOfReportsByMarket[_market] += 1;
        return true;
    }

    function isForkingMarketFinalized() public afterInitialized constant returns (bool) {
        return getBranch().getForkingMarket().getReportingState() == IMarket.ReportingState.FINALIZED;
    }
}
