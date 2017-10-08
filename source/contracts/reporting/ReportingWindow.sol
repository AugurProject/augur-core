// Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE

pragma solidity 0.4.17;


import 'reporting/IReportingWindow.sol';
import 'libraries/DelegationTarget.sol';
import 'libraries/Typed.sol';
import 'libraries/Initializable.sol';
import 'libraries/collections/Set.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReputationToken.sol';
import 'reporting/IRegistrationToken.sol';
import 'reporting/IMarket.sol';
import 'reporting/IReportingToken.sol';
import 'trading/ICash.sol';
import 'factories/MarketFactory.sol';
import 'factories/RegistrationTokenFactory.sol';
import 'reporting/Reporting.sol';
import 'libraries/math/SafeMathUint256.sol';
import 'libraries/math/RunningAverage.sol';


contract ReportingWindow is DelegationTarget, Typed, Initializable, IReportingWindow {
    using SafeMathUint256 for uint256;
    using Set for Set.Data;
    using RunningAverage for RunningAverage.Data;

    struct ReportingStatus {
        Set.Data marketsReportedOn;
        bool finishedReporting;
    }

    IUniverse private universe;
    uint256 private startTime;
    IRegistrationToken private registrationToken;
    Set.Data private markets;
    Set.Data private limitedReporterMarkets;
    Set.Data private allReporterMarkets;
    uint256 private invalidMarketCount;
    uint256 private incorrectDesignatedReportMarketCount;
    mapping(address => ReportingStatus) private reporterStatus;
    mapping(address => uint256) private numberOfReportsByMarket;
    uint256 private constant BASE_MINIMUM_REPORTERS_PER_MARKET = 7;
    RunningAverage.Data private reportingGasPrice;
    RunningAverage.Data private marketReports;
    uint256 private totalWinningReportingTokens;

    function initialize(IUniverse _universe, uint256 _reportingWindowId) public beforeInitialized returns (bool) {
        endInitialization();
        universe = _universe;
        startTime = _reportingWindowId * universe.getReportingPeriodDurationInSeconds();
        RegistrationTokenFactory _registrationTokenFactory = RegistrationTokenFactory(controller.lookup("RegistrationTokenFactory"));
        registrationToken = _registrationTokenFactory.createRegistrationToken(controller, this);
        // Initialize these to some reasonable value to handle the first market ever created without branching code 
        reportingGasPrice.record(Reporting.defaultReportingGasPrice());
        marketReports.record(Reporting.defaultReportsPerMarket());
        return true;
    }

    function createNewMarket(uint256 _endTime, uint8 _numOutcomes, uint256 _numTicks, uint256 _feePerEthInWei, ICash _denominationToken, address _creator, address _designatedReporterAddress) public afterInitialized payable returns (IMarket _newMarket) {
        require(block.timestamp < startTime);
        require(universe.getReportingWindowByMarketEndTime(_endTime, _designatedReporterAddress != 0).getTypeName() == "ReportingWindow");
        _newMarket = MarketFactory(controller.lookup("MarketFactory")).createMarket.value(msg.value)(controller, this, _endTime, _numOutcomes, _numTicks, _feePerEthInWei, _denominationToken, _creator, _designatedReporterAddress);
        markets.add(_newMarket);
        limitedReporterMarkets.add(_newMarket);
        return _newMarket;
    }

    function migrateMarketInFromSibling() public afterInitialized returns (bool) {
        IMarket _market = IMarket(msg.sender);
        IReportingWindow _shadyReportingWindow = _market.getReportingWindow();
        require(universe.isContainerForReportingWindow(_shadyReportingWindow));
        IReportingWindow _originalReportingWindow = _shadyReportingWindow;
        require(_originalReportingWindow.isContainerForMarket(_market));
        privateAddMarket(_market);
        return true;
    }

    function migrateMarketInFromNibling() public afterInitialized returns (bool) {
        IMarket _shadyMarket = IMarket(msg.sender);
        IUniverse _shadyUniverse = _shadyMarket.getUniverse();
        require(_shadyUniverse == universe.getParentUniverse());
        IUniverse _originalUniverse = _shadyUniverse;
        IReportingWindow _shadyReportingWindow = _shadyMarket.getReportingWindow();
        require(_originalUniverse.isContainerForReportingWindow(_shadyReportingWindow));
        IReportingWindow _originalReportingWindow = _shadyReportingWindow;
        require(_originalReportingWindow.isContainerForMarket(_shadyMarket));
        IMarket _legitMarket = _shadyMarket;
        _originalReportingWindow.migrateFeesDueToFork();
        privateAddMarket(_legitMarket);
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

        if (_state == IMarket.ReportingState.ALL_REPORTING) {
            allReporterMarkets.add(_market);
        } else {
            allReporterMarkets.remove(_market);
        }

        if (_state == IMarket.ReportingState.LIMITED_REPORTING) {
            limitedReporterMarkets.add(_market);
        } else {
            limitedReporterMarkets.remove(_market);
        }

        if (_state == IMarket.ReportingState.FINALIZED) {
            if (!_market.isValid()) {
                invalidMarketCount++;
            }
            if (_market.getFinalPayoutDistributionHash() != _market.getDesignatedReportPayoutHash()) {
                incorrectDesignatedReportMarketCount++;
            }
            marketReports.record(numberOfReportsByMarket[_market]);
            uint256 _totalWinningReportingTokens = _market.getFinalWinningReportingToken().totalSupply();
            totalWinningReportingTokens = totalWinningReportingTokens.add(_totalWinningReportingTokens);
        }

        return true;
    }

    function noteReport(IMarket _market, address _reporter, bytes32 _payoutDistributionHash) public afterInitialized returns (bool) {
        require(markets.contains(_market));
        require(_market.getReportingTokenOrZeroByPayoutDistributionHash(_payoutDistributionHash) == msg.sender);
        IMarket.ReportingState _state = _market.getReportingState();
        require(_state == IMarket.ReportingState.ALL_REPORTING
            || _state == IMarket.ReportingState.LIMITED_REPORTING
            || _state == IMarket.ReportingState.DESIGNATED_REPORTING);
        if (_state == IMarket.ReportingState.ALL_REPORTING) {
            // always give credit for events in all-reporters phase
            privateNoteReport(_market, _reporter);
        } else if (_state == IMarket.ReportingState.DESIGNATED_REPORTING) {
            privateNoteReport(_market, _reporter);
        } else if (numberOfReportsByMarket[_market] < getMaxReportsPerLimitedReporterMarket()) {
            // only give credit for limited reporter markets up to the max reporters for that market
            privateNoteReport(_market, _reporter);
        }
        // no credit in all other cases (but user can still report)
        return true;
    }

    function getAvgReportingGasCost() public returns (uint256) {
        return reportingGasPrice.currentAverage();
    }

    function getAvgReportsPerMarket() public returns (uint256) {
        return marketReports.currentAverage();
    }

    function getTypeName() public afterInitialized view returns (bytes32) {
        return "ReportingWindow";
    }

    function getUniverse() public afterInitialized view returns (IUniverse) {
        return universe;
    }

    function getRegistrationToken() public afterInitialized view returns (IRegistrationToken) {
        return registrationToken;
    }

    function getReputationToken() public afterInitialized view returns (IReputationToken) {
        return universe.getReputationToken();
    }

    function getStartTime() public afterInitialized view returns (uint256) {
        return startTime;
    }

    function getEndTime() public afterInitialized view returns (uint256) {
        return getDisputeEndTime();
    }

    function getNumMarkets() public afterInitialized view returns (uint256) {
        return markets.count;
    }

    function getNumInvalidMarkets() public afterInitialized view returns (uint256) {
        return invalidMarketCount;
    }

    function getNumIncorrectDesignatedReportMarkets() public view returns (uint256) {
        return incorrectDesignatedReportMarketCount;
    }

    function getReportingStartTime() public afterInitialized view returns (uint256) {
        return getStartTime();
    }

    function getReportingEndTime() public afterInitialized view returns (uint256) {
        return getStartTime() + Reporting.reportingDurationSeconds();
    }

    function getDisputeStartTime() public afterInitialized view returns (uint256) {
        return getReportingEndTime();
    }

    function getDisputeEndTime() public afterInitialized view returns (uint256) {
        return getDisputeStartTime() + Reporting.reportingDisputeDurationSeconds();
    }

    function getNextReportingWindow() public returns (IReportingWindow) {
        uint256 _nextTimestamp = getEndTime() + 1;
        return getUniverse().getReportingWindowByTimestamp(_nextTimestamp);
    }

    function getPreviousReportingWindow() public returns (IReportingWindow) {
        uint256 _previousTimestamp = getStartTime() - 1;
        return getUniverse().getReportingWindowByTimestamp(_previousTimestamp);
    }

    function checkIn() public afterInitialized returns (bool) {
        uint256 _totalReportableMarkets = getLimitedReporterMarketsCount() + getAllReporterMarketsCount();
        require(_totalReportableMarkets < 1);
        require(isActive());
        require(getRegistrationToken().balanceOf(msg.sender) > 0);
        reporterStatus[msg.sender].finishedReporting = true;
        return true;
    }

    // This exists as an edge case handler for when a ReportingWindow has no markets but we want to migrate fees to a new universe. If a market exists it should be migrated and that will trigger a fee migration. Otherwise calling this on the desitnation reporting window in the forked universe with the old reporting window as an argument will trigger a fee migration manaully
    function triggerMigrateFeesDueToFork(IReportingWindow _reportingWindow) public afterInitialized returns (bool) {
        require(_reportingWindow.getNumMarkets() == 0);
        _reportingWindow.migrateFeesDueToFork();
    }

    function migrateFeesDueToFork() public afterInitialized returns (bool) {
        require(isForkingMarketFinalized());
        // NOTE: Will need to figure out a way to transfer other denominations when that is implemented
        ICash _cash = ICash(controller.lookup("Cash"));
        uint256 _balance = _cash.balanceOf(this);
        if (_balance == 0) {
            return false;
        }
        IReportingWindow _shadyReportingWindow = IReportingWindow(msg.sender);
        IUniverse _shadyUniverse = _shadyReportingWindow.getUniverse();
        require(_shadyUniverse.isContainerForReportingWindow(_shadyReportingWindow));
        require(universe.isParentOf(_shadyUniverse));
        IUniverse _destinationUniverse = _shadyUniverse;
        IReportingWindow _destinationReportingWindow = _shadyReportingWindow;
        bytes32 _winningForkPayoutDistributionHash = universe.getForkingMarket().getFinalPayoutDistributionHash();
        require(_destinationUniverse == universe.getChildUniverse(_winningForkPayoutDistributionHash));
        _cash.transfer(_destinationReportingWindow, _balance);
        return true;
    }

    function isActive() public afterInitialized view returns (bool) {
        if (block.timestamp <= getStartTime()) {
            return false;
        }
        if (block.timestamp >= getEndTime()) {
            return false;
        }
        return true;
    }

    function isReportingActive() public afterInitialized view returns (bool) {
        if (block.timestamp <= getStartTime()) {
            return false;
        }
        if (block.timestamp >= getReportingEndTime()) {
            return false;
        }
        return true;
    }

    function isDisputeActive() public afterInitialized view returns (bool) {
        if (block.timestamp <= getDisputeStartTime()) {
            return false;
        }
        if (block.timestamp >= getEndTime()) {
            return false;
        }
        return true;
    }

    function getTargetReportsPerLimitedReporterMarket() public afterInitialized view returns (uint256) {
        uint256 _limitedReporterMarketCount = limitedReporterMarkets.count;
        if (_limitedReporterMarketCount == 0) {
            return 0;
        }

        uint256 _registeredReporters = registrationToken.getPeakSupply();
        uint256 _minimumReportsPerMarket = BASE_MINIMUM_REPORTERS_PER_MARKET;
        uint256 _totalReportsForAllLimitedReporterMarkets = _minimumReportsPerMarket * _limitedReporterMarketCount;

        if (_registeredReporters > _totalReportsForAllLimitedReporterMarkets) {
            uint256 _factor = _registeredReporters / _totalReportsForAllLimitedReporterMarkets;
            _minimumReportsPerMarket = _minimumReportsPerMarket * _factor;
        }

        return _minimumReportsPerMarket;
    }

    function getMaxReportsPerLimitedReporterMarket() public afterInitialized view returns (uint256) {
        return getTargetReportsPerLimitedReporterMarket() + 2;
    }

    function getRequiredReportsPerReporterForlimitedReporterMarkets() public afterInitialized view returns (uint256) {
        uint256 _numLimitedReporterMarkets = limitedReporterMarkets.count;
        uint256 _requiredReports = getTargetReportsPerLimitedReporterMarket() * _numLimitedReporterMarkets / registrationToken.totalSupply();
        // We shouldn't require more reporting than is possible.
        return _requiredReports.min(_numLimitedReporterMarkets);
    }

    function getTargetReportsPerReporter() public afterInitialized view returns (uint256) {
        uint256 _limitedMarketReportsPerReporter = getRequiredReportsPerReporterForlimitedReporterMarkets();
        return allReporterMarkets.count + _limitedMarketReportsPerReporter;
    }

    function getMarketsCount() public afterInitialized view returns (uint256) {
        return markets.count;
    }

    function getLimitedReporterMarketsCount() public afterInitialized view returns (uint256) {
        return limitedReporterMarkets.count;
    }

    function getAllReporterMarketsCount() public afterInitialized view returns (uint256) {
        return allReporterMarkets.count;
    }

    function isContainerForRegistrationToken(IRegistrationToken _shadyRegistrationToken) public afterInitialized view returns (bool) {
        if (_shadyRegistrationToken.getTypeName() != "RegistrationToken") {
            return false;
        }
        return registrationToken == _shadyRegistrationToken;
    }

    function isContainerForMarket(IMarket _shadyMarket) public afterInitialized returns (bool) {
        if (_shadyMarket.getTypeName() != "Market") {
            return false;
        }
        return markets.contains(_shadyMarket);
    }

    function isDoneReporting(address _reporter) public afterInitialized view returns (bool) {
        return reporterStatus[_reporter].finishedReporting;
    }

    function privateAddMarket(IMarket _market) private afterInitialized returns (bool) {
        require(!markets.contains(_market));
        require(!limitedReporterMarkets.contains(_market));
        require(!allReporterMarkets.contains(_market));
        markets.add(_market);
        return true;
    }

    function privateNoteReport(IMarket _market, address _reporter) private afterInitialized returns (bool) {
        Set.Data storage marketsReportedOn = reporterStatus[_reporter].marketsReportedOn;
        if (!marketsReportedOn.add(_market)) {
            return true;
        }
        if (marketsReportedOn.count >= getTargetReportsPerReporter()) {
            reporterStatus[_reporter].finishedReporting = true;
        }
        numberOfReportsByMarket[_market] += 1;
        reportingGasPrice.record(tx.gasprice);
        return true;
    }

    function isForkingMarketFinalized() public afterInitialized view returns (bool) {
        return getUniverse().getForkingMarket().getReportingState() == IMarket.ReportingState.FINALIZED;
    }
}
