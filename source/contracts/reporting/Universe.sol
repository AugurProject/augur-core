pragma solidity 0.4.24;


import 'reporting/IUniverse.sol';
import 'Controlled.sol';
import 'libraries/ITyped.sol';
import 'factories/IReputationTokenFactory.sol';
import 'factories/DisputeWindowFactory.sol';
import 'factories/MarketFactory.sol';
import 'factories/IAuctionFactory.sol';
import 'reporting/IMarket.sol';
import 'reporting/IV2ReputationToken.sol';
import 'reporting/IAuction.sol';
import 'reporting/IDisputeWindow.sol';
import 'reporting/Reporting.sol';
import 'reporting/IRepPriceOracle.sol';
import 'libraries/math/SafeMathUint256.sol';
import 'IAugur.sol';


contract Universe is Controlled, ITyped, IUniverse {
    using SafeMathUint256 for uint256;

    IUniverse private parentUniverse;
    bytes32 private parentPayoutDistributionHash;
    IV2ReputationToken private reputationToken;
    IAuction private auction;
    IMarket private forkingMarket;
    bytes32 private tentativeWinningChildUniversePayoutDistributionHash;
    uint256 private forkEndTime;
    uint256 private forkReputationGoal;
    uint256 private disputeThresholdForFork;
    uint256 private disputeThresholdForDisputePacing;
    uint256 private initialReportMinValue;
    mapping(uint256 => IDisputeWindow) private disputeWindows;
    mapping(address => bool) private markets;
    mapping(bytes32 => IUniverse) private childUniverses;
    uint256 private openInterestInAttoEth;

    mapping (address => uint256) private validityBondInAttoEth;
    mapping (address => uint256) private targetReporterGasCosts;
    mapping (address => uint256) private designatedReportStakeInAttoRep;
    mapping (address => uint256) private designatedReportNoShowBondInAttoRep;
    mapping (address => uint256) private shareSettlementFeeDivisor;

    constructor(IController _controller, IUniverse _parentUniverse, bytes32 _parentPayoutDistributionHash) public {
        controller = _controller;
        parentUniverse = _parentUniverse;
        parentPayoutDistributionHash = _parentPayoutDistributionHash;
        reputationToken = IV2ReputationToken(IReputationTokenFactory(controller.lookup("ReputationTokenFactory")).createReputationToken(controller, this, parentUniverse));
        auction = IAuctionFactory(controller.lookup("AuctionFactory")).createAuction(controller, this, reputationToken);
        updateForkValues();
        require(reputationToken != address(0));
    }

    function fork() public returns (bool) {
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
        disputeThresholdForDisputePacing = disputeThresholdForFork.div(2**5); // Disputes begin normal pacing once there are 4 rounds remaining in the fastest case to fork. The "last" round is the one that causes a fork and requires no time so the exponent here is 5 to provide for that many rounds actually occuring.
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

    function getReputationToken() public view returns (IV2ReputationToken) {
        return reputationToken;
    }

    function getAuction() public view returns (IAuction) {
        return auction;
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

    function getDisputeThresholdForDisputePacing() public view returns (uint256) {
        return disputeThresholdForDisputePacing;
    }

    function getInitialReportMinValue() public view returns (uint256) {
        return initialReportMinValue;
    }

    function getDisputeWindow(uint256 _disputeWindowId) public view returns (IDisputeWindow) {
        return disputeWindows[_disputeWindowId];
    }

    function isForking() public view returns (bool) {
        return forkingMarket != IMarket(0);
    }

    function getChildUniverse(bytes32 _parentPayoutDistributionHash) public view returns (IUniverse) {
        return childUniverses[_parentPayoutDistributionHash];
    }

    function getDisputeWindowId(uint256 _timestamp) public view returns (uint256) {
        return _timestamp.div(getDisputeRoundDurationInSeconds());
    }

    function getDisputeRoundDurationInSeconds() public view returns (uint256) {
        return Reporting.getDisputeRoundDurationSeconds();
    }

    function getOrCreateDisputeWindowByTimestamp(uint256 _timestamp) public returns (IDisputeWindow) {
        uint256 _windowId = getDisputeWindowId(_timestamp);
        if (disputeWindows[_windowId] == address(0)) {
            IDisputeWindow _disputeWindow = DisputeWindowFactory(controller.lookup("DisputeWindowFactory")).createDisputeWindow(controller, this, _windowId);
            disputeWindows[_windowId] = _disputeWindow;
            controller.getAugur().logDisputeWindowCreated(_disputeWindow, _windowId);
        }
        return disputeWindows[_windowId];
    }

    function getDisputeWindowByTimestamp(uint256 _timestamp) public view returns (IDisputeWindow) {
        uint256 _windowId = getDisputeWindowId(_timestamp);
        return disputeWindows[_windowId];
    }

    function getOrCreatePreviousPreviousDisputeWindow() public returns (IDisputeWindow) {
        return getOrCreateDisputeWindowByTimestamp(controller.getTimestamp().sub(getDisputeRoundDurationInSeconds().mul(2)));
    }

    function getOrCreatePreviousDisputeWindow() public returns (IDisputeWindow) {
        return getOrCreateDisputeWindowByTimestamp(controller.getTimestamp().sub(getDisputeRoundDurationInSeconds()));
    }

    function getPreviousDisputeWindow() public view returns (IDisputeWindow) {
        return getDisputeWindowByTimestamp(controller.getTimestamp().sub(getDisputeRoundDurationInSeconds()));
    }

    function getOrCreateCurrentDisputeWindow() public returns (IDisputeWindow) {
        return getOrCreateDisputeWindowByTimestamp(controller.getTimestamp());
    }

    function getCurrentDisputeWindow() public view returns (IDisputeWindow) {
        return getDisputeWindowByTimestamp(controller.getTimestamp());
    }

    function getOrCreateNextDisputeWindow() public returns (IDisputeWindow) {
        return getOrCreateDisputeWindowByTimestamp(controller.getTimestamp().add(getDisputeRoundDurationInSeconds()));
    }

    function getNextDisputeWindow() public view returns (IDisputeWindow) {
        return getDisputeWindowByTimestamp(controller.getTimestamp().add(getDisputeRoundDurationInSeconds()));
    }

    function getOrCreateDisputeWindowBefore(IDisputeWindow _disputeWindow) public returns (IDisputeWindow) {
        return getOrCreateDisputeWindowByTimestamp(_disputeWindow.getStartTime().sub(2));
    }

    function createChildUniverse(uint256[] _parentPayoutNumerators) public returns (IUniverse) {
        bytes32 _parentPayoutDistributionHash = forkingMarket.derivePayoutDistributionHash(_parentPayoutNumerators);
        IUniverse _childUniverse = getChildUniverse(_parentPayoutDistributionHash);
        IAugur _augur = controller.getAugur();
        if (_childUniverse == IUniverse(0)) {
            _childUniverse = _augur.createChildUniverse(_parentPayoutDistributionHash, _parentPayoutNumerators);
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

    function isContainerForDisputeWindow(IDisputeWindow _shadyDisputeWindow) public view returns (bool) {
        uint256 _startTime = _shadyDisputeWindow.getStartTime();
        if (_startTime == 0) {
            return false;
        }
        uint256 _disputeWindowId = getDisputeWindowId(_startTime);
        IDisputeWindow _legitDisputeWindow = disputeWindows[_disputeWindowId];
        return _shadyDisputeWindow == _legitDisputeWindow;
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

    function decrementOpenInterest(uint256 _amount) public onlyWhitelistedCallers returns (bool) {
        openInterestInAttoEth = openInterestInAttoEth.sub(_amount);
        return true;
    }

    function decrementOpenInterestFromMarket(uint256 _amount) public returns (bool) {
        require(isContainerForMarket(IMarket(msg.sender)));
        openInterestInAttoEth = openInterestInAttoEth.sub(_amount);
        return true;
    }

    function incrementOpenInterest(uint256 _amount) public onlyWhitelistedCallers returns (bool) {
        openInterestInAttoEth = openInterestInAttoEth.add(_amount);
        return true;
    }

    function incrementOpenInterestFromMarket(uint256 _amount) public returns (bool) {
        require(isContainerForMarket(IMarket(msg.sender)));
        openInterestInAttoEth = openInterestInAttoEth.add(_amount);
        return true;
    }

    function getOpenInterestInAttoEth() public view returns (uint256) {
        return openInterestInAttoEth;
    }

    function getRepMarketCapInAttoEth() public view returns (uint256) {
        uint256 _attoEthPerRep = auction.getRepPriceInAttoEth();
        uint256 _repMarketCapInAttoEth = getReputationToken().totalSupply().mul(_attoEthPerRep).div(10 ** 18);
        return _repMarketCapInAttoEth;
    }

    function getTargetRepMarketCapInAttoEth() public view returns (uint256) {
        return getOpenInterestInAttoEth().mul(Reporting.getTargetRepMarketCapMultiplier()).div(Reporting.getTargetRepMarketCapDivisor());
    }

    function getOrCacheValidityBond() public returns (uint256) {
        IDisputeWindow _disputeWindow = getOrCreateCurrentDisputeWindow();
        IDisputeWindow  _previousDisputeWindow = getOrCreatePreviousPreviousDisputeWindow();
        uint256 _currentValidityBondInAttoEth = validityBondInAttoEth[_disputeWindow];
        if (_currentValidityBondInAttoEth != 0) {
            return _currentValidityBondInAttoEth;
        }
        uint256 _totalMarketsInPreviousWindow = _previousDisputeWindow.getNumMarkets();
        uint256 _invalidMarketsInPreviousWindow = _previousDisputeWindow.getNumInvalidMarkets();
        uint256 _previousValidityBondInAttoEth = validityBondInAttoEth[_previousDisputeWindow];
        _currentValidityBondInAttoEth = calculateFloatingValue(_invalidMarketsInPreviousWindow, _totalMarketsInPreviousWindow, Reporting.getTargetInvalidMarketsDivisor(), _previousValidityBondInAttoEth, Reporting.getDefaultValidityBond(), Reporting.getValidityBondFloor());
        validityBondInAttoEth[_disputeWindow] = _currentValidityBondInAttoEth;
        return _currentValidityBondInAttoEth;
    }

    function getOrCacheDesignatedReportStake() public returns (uint256) {
        IDisputeWindow _disputeWindow = getOrCreateCurrentDisputeWindow();
        IDisputeWindow _previousDisputeWindow = getOrCreatePreviousPreviousDisputeWindow();
        uint256 _currentDesignatedReportStakeInAttoRep = designatedReportStakeInAttoRep[_disputeWindow];
        if (_currentDesignatedReportStakeInAttoRep != 0) {
            return _currentDesignatedReportStakeInAttoRep;
        }
        uint256 _totalMarketsInPreviousWindow = _previousDisputeWindow.getNumMarkets();
        uint256 _incorrectDesignatedReportMarketsInPreviousWindow = _previousDisputeWindow.getNumIncorrectDesignatedReportMarkets();
        uint256 _previousDesignatedReportStakeInAttoRep = designatedReportStakeInAttoRep[_previousDisputeWindow];

        _currentDesignatedReportStakeInAttoRep = calculateFloatingValue(_incorrectDesignatedReportMarketsInPreviousWindow, _totalMarketsInPreviousWindow, Reporting.getTargetIncorrectDesignatedReportMarketsDivisor(), _previousDesignatedReportStakeInAttoRep, initialReportMinValue, initialReportMinValue);
        designatedReportStakeInAttoRep[_disputeWindow] = _currentDesignatedReportStakeInAttoRep;
        return _currentDesignatedReportStakeInAttoRep;
    }

    function getOrCacheDesignatedReportNoShowBond() public returns (uint256) {
        IDisputeWindow _disputeWindow = getOrCreateCurrentDisputeWindow();
        IDisputeWindow _previousDisputeWindow = getOrCreatePreviousPreviousDisputeWindow();
        uint256 _currentDesignatedReportNoShowBondInAttoRep = designatedReportNoShowBondInAttoRep[_disputeWindow];
        if (_currentDesignatedReportNoShowBondInAttoRep != 0) {
            return _currentDesignatedReportNoShowBondInAttoRep;
        }
        uint256 _totalMarketsInPreviousWindow = _previousDisputeWindow.getNumMarkets();
        uint256 _designatedReportNoShowsInPreviousWindow = _previousDisputeWindow.getNumDesignatedReportNoShows();
        uint256 _previousDesignatedReportNoShowBondInAttoRep = designatedReportNoShowBondInAttoRep[_previousDisputeWindow];

        _currentDesignatedReportNoShowBondInAttoRep = calculateFloatingValue(_designatedReportNoShowsInPreviousWindow, _totalMarketsInPreviousWindow, Reporting.getTargetDesignatedReportNoShowsDivisor(), _previousDesignatedReportNoShowBondInAttoRep, initialReportMinValue, initialReportMinValue);
        designatedReportNoShowBondInAttoRep[_disputeWindow] = _currentDesignatedReportNoShowBondInAttoRep;
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

    function getOrCacheReportingFeeDivisor() public returns (uint256) {
        IDisputeWindow _disputeWindow = getOrCreateCurrentDisputeWindow();
        IDisputeWindow _previousDisputeWindow = getOrCreatePreviousDisputeWindow();
        uint256 _currentFeeDivisor = shareSettlementFeeDivisor[_disputeWindow];
        if (_currentFeeDivisor != 0) {
            return _currentFeeDivisor;
        }
        uint256 _repMarketCapInAttoEth = getRepMarketCapInAttoEth();
        uint256 _targetRepMarketCapInAttoEth = getTargetRepMarketCapInAttoEth();
        uint256 _previousFeeDivisor = shareSettlementFeeDivisor[_previousDisputeWindow];
        if (_previousFeeDivisor == 0) {
            _currentFeeDivisor = Reporting.getDefaultReportingFeeDivisor();
        } else if (_targetRepMarketCapInAttoEth == 0) {
            _currentFeeDivisor = Reporting.getDefaultReportingFeeDivisor();
        } else {
            _currentFeeDivisor = _previousFeeDivisor.mul(_repMarketCapInAttoEth).div(_targetRepMarketCapInAttoEth);
        }

        _currentFeeDivisor = _currentFeeDivisor
            .max(Reporting.getMinimumReportingFeeDivisor())
            .min(Reporting.getMaximumReportingFeeDivisor());

        shareSettlementFeeDivisor[_disputeWindow] = _currentFeeDivisor;
        return _currentFeeDivisor;
    }

    function getOrCacheMarketCreationCost() public returns (uint256) {
        return getOrCacheValidityBond();
    }

    function getInitialReportStakeSize() public returns (uint256) {
        return getOrCacheDesignatedReportNoShowBond().max(getOrCacheDesignatedReportStake());
    }

    function createYesNoMarket(uint256 _endTime, uint256 _feePerEthInWei, address _designatedReporterAddress, bytes32 _topic, string _description, string _extraInfo) public payable returns (IMarket _newMarket) {
        require(bytes(_description).length > 0);
        _newMarket = createMarketInternal(_endTime, _feePerEthInWei, _designatedReporterAddress, msg.sender, 2, 10000);
        controller.getAugur().logMarketCreated(_topic, _description, _extraInfo, this, _newMarket, msg.sender, 0, 1 ether, IMarket.MarketType.YES_NO);
        return _newMarket;
    }

    function createCategoricalMarket(uint256 _endTime, uint256 _feePerEthInWei, address _designatedReporterAddress, bytes32[] _outcomes, bytes32 _topic, string _description, string _extraInfo) public payable returns (IMarket _newMarket) {
        require(bytes(_description).length > 0);
        _newMarket = createMarketInternal(_endTime, _feePerEthInWei, _designatedReporterAddress, msg.sender, uint256(_outcomes.length), 10000);
        controller.getAugur().logMarketCreated(_topic, _description, _extraInfo, this, _newMarket, msg.sender, _outcomes, 0, 1 ether, IMarket.MarketType.CATEGORICAL);
        return _newMarket;
    }

    function createScalarMarket(uint256 _endTime, uint256 _feePerEthInWei, address _designatedReporterAddress, int256 _minPrice, int256 _maxPrice, uint256 _numTicks, bytes32 _topic, string _description, string _extraInfo) public payable returns (IMarket _newMarket) {
        require(bytes(_description).length > 0);
        require(_minPrice < _maxPrice);
        require(_numTicks.isMultipleOf(2));
        _newMarket = createMarketInternal(_endTime, _feePerEthInWei, _designatedReporterAddress, msg.sender, 2, _numTicks);
        controller.getAugur().logMarketCreated(_topic, _description, _extraInfo, this, _newMarket, msg.sender, _minPrice, _maxPrice, IMarket.MarketType.SCALAR);
        return _newMarket;
    }

    function createMarketInternal(uint256 _endTime, uint256 _feePerEthInWei, address _designatedReporterAddress, address _sender, uint256 _numOutcomes, uint256 _numTicks) private returns (IMarket _newMarket) {
        MarketFactory _marketFactory = MarketFactory(controller.lookup("MarketFactory"));
        getReputationToken().trustedUniverseTransfer(_sender, _marketFactory, getOrCacheDesignatedReportNoShowBond());
        _newMarket = _marketFactory.createMarket.value(msg.value)(controller, this, _endTime, _feePerEthInWei, _designatedReporterAddress, _sender, _numOutcomes, _numTicks);
        markets[address(_newMarket)] = true;
        return _newMarket;
    }

    function redeemStake(IReportingParticipant[] _reportingParticipants) public returns (bool) {
        for (uint256 i=0; i < _reportingParticipants.length; i++) {
            _reportingParticipants[i].redeem(msg.sender);
        }
        return true;
    }
}
