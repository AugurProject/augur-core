pragma solidity 0.4.20;


import 'reporting/IUniverse.sol';
import 'libraries/DelegationTarget.sol';
import 'libraries/ITyped.sol';
import 'libraries/Initializable.sol';
import 'factories/ReputationTokenFactory.sol';
import 'factories/FeeWindowFactory.sol';
import 'factories/MarketFactory.sol';
import 'reporting/IMarket.sol';
import 'reporting/IReputationToken.sol';
import 'reporting/IFeeWindow.sol';
import 'reporting/IFeeToken.sol';
import 'reporting/Reporting.sol';
import 'reporting/IRepPriceOracle.sol';
import 'libraries/math/SafeMathUint256.sol';
import 'IAugur.sol';


contract Universe is DelegationTarget, ITyped, Initializable, IUniverse {
    using SafeMathUint256 for uint256;

    IUniverse private parentUniverse;
    bytes32 private parentPayoutDistributionHash;
    IReputationToken private reputationToken;
    IMarket private forkingMarket;
    bytes32 private tentativeWinningChildUniversePayoutDistributionHash;
    uint256 private forkEndTime;
    uint256 private forkReputationGoal;
    uint256 private disputeThresholdForFork;
    uint256 private initialReportMinValue;
    mapping(uint256 => IFeeWindow) private feeWindows;
    mapping(address => bool) private markets;
    mapping(bytes32 => IUniverse) private childUniverses;
    uint256 private openInterestInAttoEth;

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
        updateForkValues();
        require(reputationToken != address(0));
        return true;
    }

    function fork() public onlyInGoodTimes afterInitialized returns (bool) {
        require(!isForking());
        require(isContainerForMarket(IMarket(msg.sender)));
        forkingMarket = IMarket(msg.sender);
        forkEndTime = controller.getTimestamp().add(Reporting.getForkDurationSeconds());
        controller.getAugur().logUniverseForked();
        return true;
    }

    function updateForkValues() public returns (bool) {
        uint256 _totalRepSupply = reputationToken.getTotalTheoreticalSupply();
        forkReputationGoal = _totalRepSupply.div(2); // 50% of REP migrating results in a victory in a fork
        disputeThresholdForFork = _totalRepSupply.div(40); // 2.5% of the total rep supply
        initialReportMinValue = disputeThresholdForFork.div(3).div(2**18).add(1); // This value will result in a maximum 20 round dispute sequence
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

    function getDisputeThresholdForFork() public view returns (uint256) {
        return disputeThresholdForFork;
    }

    function getInitialReportMinValue() public view returns (uint256) {
        return initialReportMinValue;
    }

    function getFeeWindow(uint256 _feeWindowId) public view returns (IFeeWindow) {
        return feeWindows[_feeWindowId];
    }

    function isForking() public view returns (bool) {
        return forkingMarket != IMarket(0);
    }

    function getChildUniverse(bytes32 _parentPayoutDistributionHash) public view returns (IUniverse) {
        return childUniverses[_parentPayoutDistributionHash];
    }

    function getFeeWindowId(uint256 _timestamp) public view returns (uint256) {
        return _timestamp.div(getDisputeRoundDurationInSeconds());
    }

    function getDisputeRoundDurationInSeconds() public view returns (uint256) {
        return Reporting.getDisputeRoundDurationSeconds();
    }

    function getOrCreateFeeWindowByTimestamp(uint256 _timestamp) public onlyInGoodTimes returns (IFeeWindow) {
        uint256 _windowId = getFeeWindowId(_timestamp);
        if (feeWindows[_windowId] == address(0)) {
            IFeeWindow _feeWindow = FeeWindowFactory(controller.lookup("FeeWindowFactory")).createFeeWindow(controller, this, _windowId);
            feeWindows[_windowId] = _feeWindow;
            controller.getAugur().logFeeWindowCreated(_feeWindow, _windowId);
        }
        return feeWindows[_windowId];
    }

    function getFeeWindowByTimestamp(uint256 _timestamp) public view onlyInGoodTimes returns (IFeeWindow) {
        uint256 _windowId = getFeeWindowId(_timestamp);
        return feeWindows[_windowId];
    }

    function getOrCreatePreviousFeeWindow() public onlyInGoodTimes returns (IFeeWindow) {
        return getOrCreateFeeWindowByTimestamp(controller.getTimestamp().sub(getDisputeRoundDurationInSeconds()));
    }

    function getPreviousFeeWindow() public view onlyInGoodTimes returns (IFeeWindow) {
        return getFeeWindowByTimestamp(controller.getTimestamp().sub(getDisputeRoundDurationInSeconds()));
    }

    function getOrCreateCurrentFeeWindow() public onlyInGoodTimes returns (IFeeWindow) {
        return getOrCreateFeeWindowByTimestamp(controller.getTimestamp());
    }

    function getCurrentFeeWindow() public view onlyInGoodTimes returns (IFeeWindow) {
        return getFeeWindowByTimestamp(controller.getTimestamp());
    }

    function getOrCreateNextFeeWindow() public onlyInGoodTimes returns (IFeeWindow) {
        return getOrCreateFeeWindowByTimestamp(controller.getTimestamp().add(getDisputeRoundDurationInSeconds()));
    }

    function getNextFeeWindow() public view onlyInGoodTimes returns (IFeeWindow) {
        return getFeeWindowByTimestamp(controller.getTimestamp().add(getDisputeRoundDurationInSeconds()));
    }

    function getOrCreateFeeWindowBefore(IFeeWindow _feeWindow) public onlyInGoodTimes returns (IFeeWindow) {
        return getOrCreateFeeWindowByTimestamp(_feeWindow.getStartTime().sub(2));
    }

    function createChildUniverse(uint256[] _parentPayoutNumerators, bool _parentInvalid) public returns (IUniverse) {
        bytes32 _parentPayoutDistributionHash = forkingMarket.derivePayoutDistributionHash(_parentPayoutNumerators, _parentInvalid);
        IUniverse _childUniverse = getChildUniverse(_parentPayoutDistributionHash);
        IAugur _augur = controller.getAugur();
        if (_childUniverse == IUniverse(0)) {
            _childUniverse = _augur.createChildUniverse(_parentPayoutDistributionHash, _parentPayoutNumerators, _parentInvalid);
            childUniverses[_parentPayoutDistributionHash] = _childUniverse;
        }
        return _childUniverse;
    }

    function updateTentativeWinningChildUniverse(bytes32 _parentPayoutDistributionHash) public returns (bool) {
        IUniverse _tentativeWinningUniverse = getChildUniverse(tentativeWinningChildUniversePayoutDistributionHash);
        IUniverse _updatedUniverse = getChildUniverse(_parentPayoutDistributionHash);
        uint256 _currentTentativeWinningChildUniverseRepMigrated = 0;
        if (_tentativeWinningUniverse != IUniverse(0)) {
            _currentTentativeWinningChildUniverseRepMigrated = _tentativeWinningUniverse.getReputationToken().getTotalMigrated();
        }
        uint256 _updatedUniverseRepMigrated = _updatedUniverse.getReputationToken().getTotalMigrated();
        if (_updatedUniverseRepMigrated > _currentTentativeWinningChildUniverseRepMigrated) {
            tentativeWinningChildUniversePayoutDistributionHash = _parentPayoutDistributionHash;
        }
        if (_updatedUniverseRepMigrated >= forkReputationGoal) {
            forkingMarket.finalizeFork();
        }
        return true;
    }

    function getWinningChildUniverse() public view returns (IUniverse) {
        require(isForking());
        require(tentativeWinningChildUniversePayoutDistributionHash != bytes32(0));
        IUniverse _tentativeWinningUniverse = getChildUniverse(tentativeWinningChildUniversePayoutDistributionHash);
        uint256 _winningAmount = _tentativeWinningUniverse.getReputationToken().getTotalMigrated();
        require(_winningAmount >= forkReputationGoal || controller.getTimestamp() > forkEndTime);
        return _tentativeWinningUniverse;
    }

    function isContainerForFeeWindow(IFeeWindow _shadyFeeWindow) public view returns (bool) {
        uint256 _startTime = _shadyFeeWindow.getStartTime();
        if (_startTime == 0) {
            return false;
        }
        uint256 _feeWindowId = getFeeWindowId(_startTime);
        IFeeWindow _legitFeeWindow = feeWindows[_feeWindowId];
        return _shadyFeeWindow == _legitFeeWindow;
    }

    function isContainerForFeeToken(IFeeToken _shadyFeeToken) public view returns (bool) {
        IFeeWindow _shadyFeeWindow = _shadyFeeToken.getFeeWindow();
        require(isContainerForFeeWindow(_shadyFeeWindow));
        IFeeWindow _legitFeeWindow = _shadyFeeWindow;
        return _legitFeeWindow.getFeeToken() == _shadyFeeToken;
    }

    function isContainerForMarket(IMarket _shadyMarket) public view returns (bool) {
        return markets[address(_shadyMarket)];
    }

    function addMarketTo() public returns (bool) {
        require(parentUniverse.isContainerForMarket(IMarket(msg.sender)));
        markets[msg.sender] = true;
        controller.getAugur().logMarketMigrated(IMarket(msg.sender), parentUniverse);
        return true;
    }

    function removeMarketFrom() public returns (bool) {
        require(isContainerForMarket(IMarket(msg.sender)));
        markets[msg.sender] = false;
        return true;
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

    function isContainerForReportingParticipant(IReportingParticipant _shadyReportingParticipant) public view returns (bool) {
        IMarket _shadyMarket = _shadyReportingParticipant.getMarket();
        if (_shadyMarket == address(0)) {
            return false;
        }
        if (!isContainerForMarket(_shadyMarket)) {
            return false;
        }
        IMarket _legitMarket = _shadyMarket;
        return _legitMarket.isContainerForReportingParticipant(_shadyReportingParticipant);
    }

    function isParentOf(IUniverse _shadyChild) public view returns (bool) {
        bytes32 _parentPayoutDistributionHash = _shadyChild.getParentPayoutDistributionHash();
        return getChildUniverse(_parentPayoutDistributionHash) == _shadyChild;
    }

    function decrementOpenInterest(uint256 _amount) public onlyInGoodTimes onlyWhitelistedCallers returns (bool) {
        openInterestInAttoEth = openInterestInAttoEth.sub(_amount);
        return true;
    }

    function decrementOpenInterestFromMarket(uint256 _amount) public returns (bool) {
        require(isContainerForMarket(IMarket(msg.sender)));
        openInterestInAttoEth = openInterestInAttoEth.sub(_amount);
        return true;
    }

    function incrementOpenInterest(uint256 _amount) public onlyInGoodTimes onlyWhitelistedCallers returns (bool) {
        openInterestInAttoEth = openInterestInAttoEth.add(_amount);
        return true;
    }

    function incrementOpenInterestFromMarket(uint256 _amount) public onlyInGoodTimes returns (bool) {
        require(isContainerForMarket(IMarket(msg.sender)));
        openInterestInAttoEth = openInterestInAttoEth.add(_amount);
        return true;
    }

    function getOpenInterestInAttoEth() public view returns (uint256) {
        return openInterestInAttoEth;
    }

    function getRepMarketCapInAttoeth() public view returns (uint256) {
        uint256 _attorepPerEth = IRepPriceOracle(controller.lookup("RepPriceOracle")).getRepPriceInAttoEth();
        uint256 _repMarketCapInAttoeth = getReputationToken().totalSupply().mul(_attorepPerEth);
        return _repMarketCapInAttoeth;
    }

    function getTargetRepMarketCapInAttoeth() public view returns (uint256) {
        return getOpenInterestInAttoEth().mul(Reporting.getTargetRepMarketCapMultiplier()).div(Reporting.getTargetRepMarketCapDivisor());
    }

    function getOrCacheValidityBond() public onlyInGoodTimes returns (uint256) {
        IFeeWindow _feeWindow = getOrCreateCurrentFeeWindow();
        IFeeWindow  _previousFeeWindow = getOrCreatePreviousFeeWindow();
        uint256 _currentValidityBondInAttoeth = validityBondInAttoeth[_feeWindow];
        if (_currentValidityBondInAttoeth != 0) {
            return _currentValidityBondInAttoeth;
        }
        uint256 _totalMarketsInPreviousWindow = _previousFeeWindow.getNumMarkets();
        uint256 _invalidMarketsInPreviousWindow = _previousFeeWindow.getNumInvalidMarkets();
        uint256 _previousValidityBondInAttoeth = validityBondInAttoeth[_previousFeeWindow];
        _currentValidityBondInAttoeth = calculateFloatingValue(_invalidMarketsInPreviousWindow, _totalMarketsInPreviousWindow, Reporting.getTargetInvalidMarketsDivisor(), _previousValidityBondInAttoeth, Reporting.getDefaultValidityBond(), Reporting.getValidityBondFloor());
        validityBondInAttoeth[_feeWindow] = _currentValidityBondInAttoeth;
        return _currentValidityBondInAttoeth;
    }

    function getOrCacheDesignatedReportStake() public onlyInGoodTimes returns (uint256) {
        IFeeWindow _feeWindow = getOrCreateCurrentFeeWindow();
        IFeeWindow _previousFeeWindow = getOrCreatePreviousFeeWindow();
        uint256 _currentDesignatedReportStakeInAttoRep = designatedReportStakeInAttoRep[_feeWindow];
        if (_currentDesignatedReportStakeInAttoRep != 0) {
            return _currentDesignatedReportStakeInAttoRep;
        }
        uint256 _totalMarketsInPreviousWindow = _previousFeeWindow.getNumMarkets();
        uint256 _incorrectDesignatedReportMarketsInPreviousWindow = _previousFeeWindow.getNumIncorrectDesignatedReportMarkets();
        uint256 _previousDesignatedReportStakeInAttoRep = designatedReportStakeInAttoRep[_previousFeeWindow];

        _currentDesignatedReportStakeInAttoRep = calculateFloatingValue(_incorrectDesignatedReportMarketsInPreviousWindow, _totalMarketsInPreviousWindow, Reporting.getTargetIncorrectDesignatedReportMarketsDivisor(), _previousDesignatedReportStakeInAttoRep, initialReportMinValue, initialReportMinValue);
        designatedReportStakeInAttoRep[_feeWindow] = _currentDesignatedReportStakeInAttoRep;
        return _currentDesignatedReportStakeInAttoRep;
    }

    function getOrCacheDesignatedReportNoShowBond() public onlyInGoodTimes returns (uint256) {
        IFeeWindow _feeWindow = getOrCreateCurrentFeeWindow();
        IFeeWindow _previousFeeWindow = getOrCreatePreviousFeeWindow();
        uint256 _currentDesignatedReportNoShowBondInAttoRep = designatedReportNoShowBondInAttoRep[_feeWindow];
        if (_currentDesignatedReportNoShowBondInAttoRep != 0) {
            return _currentDesignatedReportNoShowBondInAttoRep;
        }
        uint256 _totalMarketsInPreviousWindow = _previousFeeWindow.getNumMarkets();
        uint256 _designatedReportNoShowsInPreviousWindow = _previousFeeWindow.getNumDesignatedReportNoShows();
        uint256 _previousDesignatedReportNoShowBondInAttoRep = designatedReportNoShowBondInAttoRep[_previousFeeWindow];

        _currentDesignatedReportNoShowBondInAttoRep = calculateFloatingValue(_designatedReportNoShowsInPreviousWindow, _totalMarketsInPreviousWindow, Reporting.getTargetDesignatedReportNoShowsDivisor(), _previousDesignatedReportNoShowBondInAttoRep, initialReportMinValue, initialReportMinValue);
        designatedReportNoShowBondInAttoRep[_feeWindow] = _currentDesignatedReportNoShowBondInAttoRep;
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
        // Safe math div is redundant so we avoid here as we're at the stack limit.
        if (_badMarkets <= _totalMarkets / _targetDivisor) {
            // FXP formula: previous_amount * actual_percent / (2 * target_percent) + 0.5;
            _newValue = _badMarkets
                .mul(_previousValue)
                .mul(_targetDivisor);
            _newValue = _newValue / _totalMarkets;
            _newValue = _newValue / 2;
            _newValue = _newValue.add(_previousValue / 2);
        } else {
            // FXP formula: previous_amount * (1/(1 - target_percent)) * (actual_percent - target_percent) + 1;
            _newValue = _targetDivisor
                .mul(_previousValue
                    .mul(_badMarkets)
                    .div(_totalMarkets)
                .sub(_previousValue / _targetDivisor));
            _newValue = _newValue / (_targetDivisor - 1);
            _newValue = _newValue.add(_previousValue);
        }
        _newValue = _newValue.max(_floor);

        return _newValue;
    }

    function getOrCacheReportingFeeDivisor() public onlyInGoodTimes returns (uint256) {
        IFeeWindow _feeWindow = getOrCreateCurrentFeeWindow();
        IFeeWindow _previousFeeWindow = getOrCreatePreviousFeeWindow();
        uint256 _currentFeeDivisor = shareSettlementFeeDivisor[_feeWindow];
        if (_currentFeeDivisor != 0) {
            return _currentFeeDivisor;
        }
        uint256 _repMarketCapInAttoeth = getRepMarketCapInAttoeth();
        uint256 _targetRepMarketCapInAttoeth = getTargetRepMarketCapInAttoeth();
        uint256 _previousFeeDivisor = shareSettlementFeeDivisor[_previousFeeWindow];
        if (_previousFeeDivisor == 0) {
            _currentFeeDivisor = Reporting.getDefaultReportingFeeDivisor();
        } else if (_targetRepMarketCapInAttoeth == 0) {
            _currentFeeDivisor = Reporting.getDefaultReportingFeeDivisor();
        } else {
            _currentFeeDivisor = _previousFeeDivisor.mul(_repMarketCapInAttoeth).div(_targetRepMarketCapInAttoeth);
        }

        _currentFeeDivisor = _currentFeeDivisor
            .max(Reporting.getMinimumReportingFeeDivisor())
            .min(Reporting.getMaximumReportingFeeDivisor());

        shareSettlementFeeDivisor[_feeWindow] = _currentFeeDivisor;
        return _currentFeeDivisor;
    }

    function getOrCacheTargetReporterGasCosts() public onlyInGoodTimes returns (uint256) {
        IFeeWindow _feeWindow = getOrCreateCurrentFeeWindow();
        IFeeWindow _previousFeeWindow = getOrCreatePreviousFeeWindow();
        uint256 _getGasToReport = targetReporterGasCosts[_feeWindow];
        if (_getGasToReport != 0) {
            return _getGasToReport;
        }

        uint256 _avgGasPrice = _previousFeeWindow.getAvgReportingGasPrice();
        _getGasToReport = Reporting.getGasToReport();
        // we double it to try and ensure we have more than enough rather than not enough
        targetReporterGasCosts[_feeWindow] = _getGasToReport.mul(_avgGasPrice).mul(2);
        return targetReporterGasCosts[_feeWindow];
    }

    function getOrCacheMarketCreationCost() public onlyInGoodTimes returns (uint256) {
        return getOrCacheValidityBond().add(getOrCacheTargetReporterGasCosts());
    }

    function getInitialReportStakeSize() public onlyInGoodTimes returns (uint256) {
        return getOrCacheDesignatedReportNoShowBond().max(getOrCacheDesignatedReportStake());
    }

    function createBinaryMarket(uint256 _endTime, uint256 _feePerEthInWei, ICash _denominationToken, address _designatedReporterAddress, bytes32 _topic, string _description, string _extraInfo) public onlyInGoodTimes afterInitialized payable returns (IMarket _newMarket) {
        require(bytes(_description).length > 0);
        _newMarket = createMarketInternal(_endTime, _feePerEthInWei, _denominationToken, _designatedReporterAddress, msg.sender, 2, 10000);
        controller.getAugur().logMarketCreated(_topic, _description, _extraInfo, this, _newMarket, msg.sender, 0, 1 ether, IMarket.MarketType.BINARY);
        return _newMarket;
    }

    function createCategoricalMarket(uint256 _endTime, uint256 _feePerEthInWei, ICash _denominationToken, address _designatedReporterAddress, bytes32[] _outcomes, bytes32 _topic, string _description, string _extraInfo) public onlyInGoodTimes afterInitialized payable returns (IMarket _newMarket) {
        require(bytes(_description).length > 0);
        _newMarket = createMarketInternal(_endTime, _feePerEthInWei, _denominationToken, _designatedReporterAddress, msg.sender, uint256(_outcomes.length), 10000);
        controller.getAugur().logMarketCreated(_topic, _description, _extraInfo, this, _newMarket, msg.sender, _outcomes, 0, 1 ether, IMarket.MarketType.CATEGORICAL);
        return _newMarket;
    }

    function createScalarMarket(uint256 _endTime, uint256 _feePerEthInWei, ICash _denominationToken, address _designatedReporterAddress, int256 _minPrice, int256 _maxPrice, uint256 _numTicks, bytes32 _topic, string _description, string _extraInfo) public onlyInGoodTimes afterInitialized payable returns (IMarket _newMarket) {
        require(bytes(_description).length > 0);
        require(_minPrice < _maxPrice);
        require(_numTicks.isMultipleOf(2));
        _newMarket = createMarketInternal(_endTime, _feePerEthInWei, _denominationToken, _designatedReporterAddress, msg.sender, 2, _numTicks);
        controller.getAugur().logMarketCreated(_topic, _description, _extraInfo, this, _newMarket, msg.sender, _minPrice, _maxPrice, IMarket.MarketType.SCALAR);
        return _newMarket;
    }

    function createMarketInternal(uint256 _endTime, uint256 _feePerEthInWei, ICash _denominationToken, address _designatedReporterAddress, address _sender, uint256 _numOutcomes, uint256 _numTicks) private onlyInGoodTimes afterInitialized returns (IMarket _newMarket) {
        MarketFactory _marketFactory = MarketFactory(controller.lookup("MarketFactory"));
        getReputationToken().trustedUniverseTransfer(_sender, _marketFactory, getOrCacheDesignatedReportNoShowBond());
        _newMarket = _marketFactory.createMarket.value(msg.value)(controller, this, _endTime, _feePerEthInWei, _denominationToken, _designatedReporterAddress, _sender, _numOutcomes, _numTicks);
        markets[address(_newMarket)] = true;
        return _newMarket;
    }

    function redeemStake(IReportingParticipant[] _reportingParticipants, IFeeWindow[] _feeWindows) public onlyInGoodTimes returns (bool) {
        for (uint256 i=0; i < _reportingParticipants.length; i++) {
            _reportingParticipants[i].redeem(msg.sender);
        }

        for (uint256 k=0; k < _feeWindows.length; k++) {
            _feeWindows[k].redeem(msg.sender);
        }

        return true;
    }

    function buyParticipationTokens(uint256 _attotokens) public onlyInGoodTimes returns (bool) {
        IFeeWindow _feeWindow = getOrCreateCurrentFeeWindow();
        _feeWindow.trustedUniverseBuy(msg.sender, _attotokens);
        return true;
    }
}
