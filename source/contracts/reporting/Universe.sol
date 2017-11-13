pragma solidity 0.4.17;


import 'reporting/IUniverse.sol';
import 'libraries/DelegationTarget.sol';
import 'libraries/ITyped.sol';
import 'libraries/Initializable.sol';
import 'factories/ReputationTokenFactory.sol';
import 'factories/ReportingWindowFactory.sol';
import 'factories/UniverseFactory.sol';
import 'reporting/IMarket.sol';
import 'reporting/IReputationToken.sol';
import 'reporting/IStakeToken.sol';
import 'reporting/IDisputeBond.sol';
import 'reporting/IReportingWindow.sol';
import 'reporting/Reporting.sol';
import 'reporting/IRepPriceOracle.sol';
import 'reporting/IParticipationToken.sol';
import 'reporting/IDisputeBond.sol';
import 'libraries/math/SafeMathUint256.sol';
import 'Augur.sol';
import 'libraries/Extractable.sol';


contract Universe is DelegationTarget, Extractable, ITyped, Initializable, IUniverse {
    using SafeMathUint256 for uint256;

    IUniverse private parentUniverse;
    bytes32 private parentPayoutDistributionHash;
    IReputationToken private reputationToken;
    IMarket private forkingMarket;
    uint256 private forkEndTime;
    uint256 private forkReputationGoal;
    mapping(uint256 => IReportingWindow) private reportingWindows;
    mapping(bytes32 => IUniverse) private childUniverses;
    uint256 private openInterestInAttoEth;
    // We increase and decrease this value seperate from the totalSupply as we do not want to count potentional infalitonary bonuses from the migration reward
    uint256 private repAvailableForExtraBondPayouts;

    mapping (address => uint256) private validityBondInAttoeth;
    mapping (address => uint256) private targetReporterGasCosts;
    mapping (address => uint256) private designatedReportStakeInAttoRep;
    mapping (address => uint256) private designatedReportNoShowBondInAttoRep;
    mapping (address => uint256) private shareSettlementFeeDivisor;

    function initialize(IUniverse _parentUniverse, bytes32 _parentPayoutDistributionHash) external onlyInGoodTimes beforeInitialized returns (bool) {
        endInitialization();
        parentUniverse = _parentUniverse;
        parentPayoutDistributionHash = _parentPayoutDistributionHash;
        reputationToken = ReputationTokenFactory(controller.lookup("ReputationTokenFactory")).createReputationToken(controller, this);
        require(reputationToken != address(0));
        return true;
    }

    function fork() public onlyInGoodTimes afterInitialized returns (bool) {
        require(forkingMarket == address(0));
        require(isContainerForMarket(IMarket(msg.sender)));
        forkingMarket = IMarket(msg.sender);
        forkEndTime = block.timestamp + Reporting.getForkDurationSeconds();
        // We pre calculate the amount of REP needed to determine a winner early in a fork. We assume maximum possible fork inflation in every fork so this is hard to achieve with every subsequent fork and may become impossible in some universes.
        if (parentUniverse != IUniverse(0)) {
            uint256 _previousForkReputationGoal = parentUniverse.getForkReputationGoal();
            forkReputationGoal = _previousForkReputationGoal + (_previousForkReputationGoal / Reporting.getForkMigrationPercentageBonusDivisor());
        } else {
            // We're using a hardcoded supply value instead of getting the total REP supply from the token since at launch we will start out with a 0 supply token and users will migrate legacy REP to this token. Since the first fork may occur before all REP migrates we want to count that unmigrated REP too since it may participate in the fork eventually.
            forkReputationGoal = Reporting.getInitialREPSupply() / Reporting.getForkRepMigrationVictoryDivisor();
        }
        controller.getAugur().logUniverseForked();
        return true;
    }

    function getTypeName() public view returns (bytes32) {
        return "Universe";
    }

    function getParentUniverse() public view returns (IUniverse) {
        return parentUniverse;
    }

    function getParentPayoutDistributionHash() public view returns (bytes32) {
        return parentPayoutDistributionHash;
    }

    function getReputationToken() public view returns (IReputationToken) {
        return reputationToken;
    }

    function getForkingMarket() public view returns (IMarket) {
        return forkingMarket;
    }

    function getForkEndTime() public view returns (uint256) {
        return forkEndTime;
    }

    function getForkReputationGoal() public view returns (uint256) {
        return forkReputationGoal;
    }

    function getReportingWindow(uint256 _reportingWindowId) public view returns (IReportingWindow) {
        return reportingWindows[_reportingWindowId];
    }

    function getChildUniverse(bytes32 _parentPayoutDistributionHash) public view returns (IUniverse) {
        return childUniverses[_parentPayoutDistributionHash];
    }

    function getReportingWindowId(uint256 _timestamp) public view returns (uint256) {
        return _timestamp / getReportingPeriodDurationInSeconds();
    }

    function getReportingPeriodDurationInSeconds() public view returns (uint256) {
        return Reporting.getReportingDurationSeconds() + Reporting.getReportingDisputeDurationSeconds();
    }

    function getOrCreateReportingWindowByTimestamp(uint256 _timestamp) public onlyInGoodTimes returns (IReportingWindow) {
        uint256 _windowId = getReportingWindowId(_timestamp);
        if (reportingWindows[_windowId] == address(0)) {
            reportingWindows[_windowId] = ReportingWindowFactory(controller.lookup("ReportingWindowFactory")).createReportingWindow(controller, this, _windowId);
        }
        return reportingWindows[_windowId];
    }

    function getReportingWindowByTimestamp(uint256 _timestamp) public view onlyInGoodTimes returns (IReportingWindow) {
        uint256 _windowId = getReportingWindowId(_timestamp);
        return reportingWindows[_windowId];
    }

    function getOrCreateReportingWindowByMarketEndTime(uint256 _endTime) public onlyInGoodTimes returns (IReportingWindow) {
        return getOrCreateReportingWindowByTimestamp(_endTime + Reporting.getDesignatedReportingDurationSeconds() + Reporting.getDesignatedReportingDisputeDurationSeconds() + 1 + getReportingPeriodDurationInSeconds());
    }

    function getReportingWindowByMarketEndTime(uint256 _endTime) public view onlyInGoodTimes returns (IReportingWindow) {
        return getReportingWindowByTimestamp(_endTime + Reporting.getDesignatedReportingDurationSeconds() + Reporting.getDesignatedReportingDisputeDurationSeconds() + 1 + getReportingPeriodDurationInSeconds());
    }

    function getOrCreatePreviousReportingWindow() public onlyInGoodTimes returns (IReportingWindow) {
        return getOrCreateReportingWindowByTimestamp(block.timestamp - getReportingPeriodDurationInSeconds());
    }

    function getPreviousReportingWindow() public view onlyInGoodTimes returns (IReportingWindow) {
        return getReportingWindowByTimestamp(block.timestamp - getReportingPeriodDurationInSeconds());
    }

    function getOrCreateCurrentReportingWindow() public onlyInGoodTimes returns (IReportingWindow) {
        return getOrCreateReportingWindowByTimestamp(block.timestamp);
    }

    function getCurrentReportingWindow() public view onlyInGoodTimes returns (IReportingWindow) {
        return getReportingWindowByTimestamp(block.timestamp);
    }

    function getOrCreateNextReportingWindow() public onlyInGoodTimes returns (IReportingWindow) {
        return getOrCreateReportingWindowByTimestamp(block.timestamp + getReportingPeriodDurationInSeconds());
    }

    function getNextReportingWindow() public view onlyInGoodTimes returns (IReportingWindow) {
        return getReportingWindowByTimestamp(block.timestamp + getReportingPeriodDurationInSeconds());
    }

    function getOrCreateChildUniverse(bytes32 _parentPayoutDistributionHash) public returns (IUniverse) {
        require(forkingMarket != IMarket(0));
        if (childUniverses[_parentPayoutDistributionHash] == address(0)) {
            childUniverses[_parentPayoutDistributionHash] = UniverseFactory(controller.lookup("UniverseFactory")).createUniverse(controller, this, _parentPayoutDistributionHash);
            controller.getAugur().logUniverseCreated(childUniverses[_parentPayoutDistributionHash]);
        }
        return childUniverses[_parentPayoutDistributionHash];
    }

    function getRepAvailableForExtraBondPayouts() public view returns (uint256) {
        return repAvailableForExtraBondPayouts;
    }

    function increaseRepAvailableForExtraBondPayouts(uint256 _amount) public onlyInGoodTimes returns (bool) {
        require(msg.sender == address(reputationToken));
        repAvailableForExtraBondPayouts = repAvailableForExtraBondPayouts.add(_amount);
        return true;
    }

    function decreaseRepAvailableForExtraBondPayouts(uint256 _amount) public onlyInGoodTimes returns (bool) {
        require(parentUniverse.isContainerForDisputeBond(IDisputeBond(msg.sender)));
        repAvailableForExtraBondPayouts = repAvailableForExtraBondPayouts.sub(_amount);
        return true;
    }

    function isContainerForReportingWindow(IReportingWindow _shadyReportingWindow) public view returns (bool) {
        uint256 _startTime = _shadyReportingWindow.getStartTime();
        if (_startTime == 0) {
            return false;
        }
        uint256 _reportingWindowId = getReportingWindowId(_startTime);
        IReportingWindow _legitReportingWindow = reportingWindows[_reportingWindowId];
        return _shadyReportingWindow == _legitReportingWindow;
    }

    function isContainerForDisputeBond(IDisputeBond _shadyDisputeBond) public view returns (bool) {
        IMarket _shadyMarket = _shadyDisputeBond.getMarket();
        if (_shadyMarket == address(0)) {
            return false;
        }
        if (!isContainerForMarket(_shadyMarket)) {
            return false;
        }
        IMarket _legitMarket = _shadyMarket;
        return _legitMarket.isContainerForDisputeBond(_shadyDisputeBond);
    }

    function isContainerForMarket(IMarket _shadyMarket) public view returns (bool) {
        IReportingWindow _shadyReportingWindow = _shadyMarket.getReportingWindow();
        if (_shadyReportingWindow == address(0)) {
            return false;
        }
        if (!isContainerForReportingWindow(_shadyReportingWindow)) {
            return false;
        }
        IReportingWindow _legitReportingWindow = _shadyReportingWindow;
        return _legitReportingWindow.isContainerForMarket(_shadyMarket);
    }

    function isContainerForStakeToken(IStakeToken _shadyStakeToken) public view returns (bool) {
        IMarket _shadyMarket = _shadyStakeToken.getMarket();
        if (_shadyMarket == address(0)) {
            return false;
        }
        if (!isContainerForMarket(_shadyMarket)) {
            return false;
        }
        IMarket _legitMarket = _shadyMarket;
        return _legitMarket.isContainerForStakeToken(_shadyStakeToken);
    }

    function isContainerForShareToken(IShareToken _shadyShareToken) public view returns (bool) {
        IMarket _shadyMarket = _shadyShareToken.getMarket();
        if (_shadyMarket == address(0)) {
            return false;
        }
        if (!isContainerForMarket(_shadyMarket)) {
            return false;
        }
        IMarket _legitMarket = _shadyMarket;
        return _legitMarket.isContainerForShareToken(_shadyShareToken);
    }

    function isContainerForParticipationToken(IParticipationToken _shadyParticipationToken) public view returns (bool) {
        IReportingWindow _shadyReportingWindow = _shadyParticipationToken.getReportingWindow();
        if (_shadyReportingWindow == address(0)) {
            return false;
        }
        if (!isContainerForReportingWindow(_shadyReportingWindow)) {
            return false;
        }
        IReportingWindow _legitReportingWindow = _shadyReportingWindow;
        return _legitReportingWindow.isContainerForParticipationToken(_shadyParticipationToken);
    }

    function isParentOf(IUniverse _shadyChild) public view returns (bool) {
        bytes32 _parentPayoutDistributionHash = _shadyChild.getParentPayoutDistributionHash();
        return childUniverses[_parentPayoutDistributionHash] == _shadyChild;
    }

    function getOrCreateReportingWindowForForkEndTime() public returns (IReportingWindow) {
        return getOrCreateReportingWindowByTimestamp(getForkEndTime());
    }

    function getReportingWindowForForkEndTime() public view returns (IReportingWindow) {
        return getReportingWindowByTimestamp(getForkEndTime());
    }

    function decrementOpenInterest(uint256 _amount) public onlyInGoodTimes onlyWhitelistedCallers returns (bool) {
        openInterestInAttoEth = openInterestInAttoEth.sub(_amount);
        return true;
    }

    // CONSIDER: It would be more correct to decrease open interest for all outstanding shares in a market when it is finalized. We aren't doing this currently since securely and correctly writing this code would require updating the Market contract, which is currently at its size limit.
    function incrementOpenInterest(uint256 _amount) public onlyInGoodTimes onlyWhitelistedCallers returns (bool) {
        openInterestInAttoEth = openInterestInAttoEth.add(_amount);
        return true;
    }

    function getOpenInterestInAttoEth() public view returns (uint256) {
        return openInterestInAttoEth;
    }

    function getRepMarketCapInAttoeth() public view returns (uint256) {
        uint256 _attorepPerEth = IRepPriceOracle(controller.lookup("RepPriceOracle")).getRepPriceInAttoEth();
        uint256 _repMarketCapInAttoeth = getReputationToken().totalSupply() * _attorepPerEth;
        return _repMarketCapInAttoeth;
    }

    function getTargetRepMarketCapInAttoeth() public view returns (uint256) {
        return getOpenInterestInAttoEth() * Reporting.getTargetRepMarketCapMultiplier();
    }

    function getOrCacheValidityBond() public onlyInGoodTimes returns (uint256) {
        IReportingWindow _reportingWindow = getOrCreateCurrentReportingWindow();
        uint256 _validityBond = getOrCacheValidityBondInternal(_reportingWindow, getOrCreatePreviousReportingWindow());
        validityBondInAttoeth[_reportingWindow] = _validityBond;
        return _validityBond;
    }

    function getValidityBond() public view onlyInGoodTimes returns (uint256) {
        return getOrCacheValidityBondInternal(getCurrentReportingWindow(), getPreviousReportingWindow());
    }

    function getOrCacheValidityBondInternal(IReportingWindow _reportingWindow, IReportingWindow _previousReportingWindow) internal view onlyInGoodTimes returns (uint256) {
        require(_reportingWindow != IReportingWindow(0));
        require(_previousReportingWindow != IReportingWindow(0));
        uint256 _currentValidityBondInAttoeth = validityBondInAttoeth[_reportingWindow];
        if (_currentValidityBondInAttoeth != 0) {
            return _currentValidityBondInAttoeth;
        }
        uint256 _totalMarketsInPreviousWindow = _previousReportingWindow.getNumMarkets();
        uint256 _invalidMarketsInPreviousWindow = _previousReportingWindow.getNumInvalidMarkets();
        uint256 _previousValidityBondInAttoeth = validityBondInAttoeth[_previousReportingWindow];
        _currentValidityBondInAttoeth = calculateFloatingValue(_invalidMarketsInPreviousWindow, _totalMarketsInPreviousWindow, Reporting.getTargetInvalidMarketsDivisor(), _previousValidityBondInAttoeth, Reporting.getDefaultValidityBond(), Reporting.getDefaultValidityBondFloor());
        return _currentValidityBondInAttoeth;
    }

    function getDesignatedReportStake() public onlyInGoodTimes returns (uint256) {
        IReportingWindow _reportingWindow = getOrCreateCurrentReportingWindow();
        uint256 _currentDesignatedReportStakeInAttoRep = designatedReportStakeInAttoRep[_reportingWindow];
        if (_currentDesignatedReportStakeInAttoRep != 0) {
            return _currentDesignatedReportStakeInAttoRep;
        }
        IReportingWindow _previousReportingWindow = getOrCreatePreviousReportingWindow();
        uint256 _totalMarketsInPreviousWindow = _previousReportingWindow.getNumMarkets();
        uint256 _incorrectDesignatedReportMarketsInPreviousWindow = _previousReportingWindow.getNumIncorrectDesignatedReportMarkets();
        uint256 _previousDesignatedReportStakeInAttoRep = designatedReportStakeInAttoRep[_previousReportingWindow];

        _currentDesignatedReportStakeInAttoRep = calculateFloatingValue(_incorrectDesignatedReportMarketsInPreviousWindow, _totalMarketsInPreviousWindow, Reporting.getTargetIncorrectDesignatedReportMarketsDivisor(), _previousDesignatedReportStakeInAttoRep, Reporting.getDefaultDesignatedReportStake(), Reporting.getDesignatedReportStakeFloor());
        designatedReportStakeInAttoRep[_reportingWindow] = _currentDesignatedReportStakeInAttoRep;
        return _currentDesignatedReportStakeInAttoRep;
    }

    function getDesignatedReportNoShowBond() public onlyInGoodTimes returns (uint256) {
        IReportingWindow _reportingWindow = getOrCreateCurrentReportingWindow();
        uint256 _currentDesignatedReportNoShowBondInAttoRep = designatedReportNoShowBondInAttoRep[_reportingWindow];
        if (_currentDesignatedReportNoShowBondInAttoRep != 0) {
            return _currentDesignatedReportNoShowBondInAttoRep;
        }
        IReportingWindow _previousReportingWindow = getOrCreatePreviousReportingWindow();
        uint256 _totalMarketsInPreviousWindow = _previousReportingWindow.getNumMarkets();
        uint256 _designatedReportNoShowsInPreviousWindow = _previousReportingWindow.getNumDesignatedReportNoShows();
        uint256 _previousDesignatedReportNoShowBondInAttoRep = designatedReportNoShowBondInAttoRep[_previousReportingWindow];

        _currentDesignatedReportNoShowBondInAttoRep = calculateFloatingValue(_designatedReportNoShowsInPreviousWindow, _totalMarketsInPreviousWindow, Reporting.getTargetDesignatedReportNoShowsDivisor(), _previousDesignatedReportNoShowBondInAttoRep, Reporting.getDefaultDesignatedReportNoShowBond(), Reporting.getDesignatedReportNoShowBondFloor());
        designatedReportNoShowBondInAttoRep[_reportingWindow] = _currentDesignatedReportNoShowBondInAttoRep;
        return _currentDesignatedReportNoShowBondInAttoRep;
    }

    function calculateFloatingValue(uint256 _badMarkets, uint256 _totalMarkets, uint256 _targetDivisor, uint256 _previousValue, uint256 _defaultValue, uint256 _floor) public pure returns (uint256 _newValue) {
        if (_totalMarkets == 0) {
            return _defaultValue;
        }
        if (_previousValue == 0) {
            _previousValue = _defaultValue;
        }

        // Modify the amount based on the previous amount and the number of markets fitting the failure criteria. We want the amount to be somewhere in the range of 0.5 to 2 times its previous value where ALL markets with the condition results in 2x and 0 results in 0.5x.
        if (_badMarkets <= _totalMarkets / _targetDivisor) {
            // FXP formula: previous_amount * actual_percent / (2 * target_percent) + 0.5;
            _newValue = _badMarkets
                .mul(_previousValue)
                .mul(_targetDivisor)
                .div(_totalMarkets)
                .div(2) + _previousValue / 2;
        } else {
            // FXP formula: previous_amount * (1/(1 - target_percent)) * (actual_percent - target_percent) + 1;
            _newValue = _targetDivisor
                .mul(_previousValue
                    .mul(_badMarkets)
                    .div(_totalMarkets)
                    .sub(_previousValue
                        .div(_targetDivisor)))
                .div(_targetDivisor - 1) + _previousValue;
        }

        if (_newValue < _floor) {
            _newValue = _floor;
        }

        return _newValue;
    }

    function getReportingFeeDivisor() public onlyInGoodTimes returns (uint256) {
        IReportingWindow _reportingWindow = getOrCreateCurrentReportingWindow();
        uint256 _currentFeeDivisor = shareSettlementFeeDivisor[_reportingWindow];
        if (_currentFeeDivisor != 0) {
            return _currentFeeDivisor;
        }
        uint256 _repMarketCapInAttoeth = getRepMarketCapInAttoeth();
        uint256 _targetRepMarketCapInAttoeth = getTargetRepMarketCapInAttoeth();
        uint256 _previousFeeDivisor = shareSettlementFeeDivisor[getOrCreatePreviousReportingWindow()];
        if (_previousFeeDivisor == 0) {
            _previousFeeDivisor = Reporting.getDefaultReportingFeeDivisor();
        }
        if (_targetRepMarketCapInAttoeth == 0) {
            _currentFeeDivisor = Reporting.getMaximumReportingFeeDivisor();
        } else {
            _currentFeeDivisor = _previousFeeDivisor * _repMarketCapInAttoeth / _targetRepMarketCapInAttoeth;
        }
        if (_currentFeeDivisor > Reporting.getMaximumReportingFeeDivisor()) {
            _currentFeeDivisor = Reporting.getMaximumReportingFeeDivisor();
        }
        shareSettlementFeeDivisor[_reportingWindow] = _currentFeeDivisor;
        return _currentFeeDivisor;
    }

    function getOrCacheTargetReporterGasCosts() public onlyInGoodTimes returns (uint256) {
        IReportingWindow _reportingWindow = getOrCreateCurrentReportingWindow();
        uint256 _reporterGasCost = getOrCacheTargetReporterGasCostsInternal(_reportingWindow, getOrCreatePreviousReportingWindow());
        targetReporterGasCosts[_reportingWindow] = _reporterGasCost;
        return _reporterGasCost;
    }

    function getTargetReporterGasCosts() public view onlyInGoodTimes returns (uint256) {
        return getOrCacheTargetReporterGasCostsInternal(getCurrentReportingWindow(), getPreviousReportingWindow());
    }

    function getOrCacheTargetReporterGasCostsInternal(IReportingWindow _reportingWindow, IReportingWindow _previousReportingWindow) internal view onlyInGoodTimes returns (uint256) {
        require(_reportingWindow != IReportingWindow(0));
        require(_previousReportingWindow != IReportingWindow(0));
        uint256 _getGasToReport = targetReporterGasCosts[_reportingWindow];
        if (_getGasToReport != 0) {
            return _getGasToReport;
        }

        uint256 _avgGasPrice = _previousReportingWindow.getAvgReportingGasPrice();
        _getGasToReport = Reporting.getGasToReport();
        // we double it to try and ensure we have more than enough rather than not enough
        return _getGasToReport * _avgGasPrice * 2;

    }

    function getMarketCreationCost() public onlyInGoodTimes returns (uint256) {
        return getOrCacheValidityBond() + getOrCacheTargetReporterGasCosts();
    }

    function getMarketCreationCostView() public view onlyInGoodTimes returns (uint256) {
        return getValidityBond() + getTargetReporterGasCosts();
    }

    function getProtectedTokens() internal returns (address[] memory) {
        return new address[](0);
    }
}
