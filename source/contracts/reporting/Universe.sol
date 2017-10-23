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


contract Universe is DelegationTarget, ITyped, Initializable, IUniverse {
    using SafeMathUint256 for uint256;

    event TokensTransferred(address indexed token, address indexed from, address indexed to, uint256 value);
    event MarketCreated(address indexed market, address indexed marketCreator, uint256 marketCreationFee, string extraInfo);
    event DesignatedReportSubmitted(address indexed reporter, address indexed market, address stakeToken, uint256 amountStaked, uint256[] payoutNumerators);
    event ReportSubmitted(address indexed reporter, address indexed market, address stakeToken, uint256 amountStaked, uint256[] payoutNumerators);
    event WinningTokensRedeemed(address indexed reporter, address indexed market, address stakeToken, uint256 amountRedeemed, uint256 reportingFeesReceived, uint256[] payoutNumerators);
    event ReportsDisputed(address indexed disputer, address indexed market, uint8 reportingPhase, uint256 disputeBondAmount);
    event MarketFinalized(address indexed market);
    event UniverseForked(address indexed universe);
    event OrderCanceled(address indexed shareToken, address indexed sender, bytes32 indexed orderId, uint8 orderType, uint256 tokenRefund, uint256 sharesRefund);
    event OrderCreated(address indexed shareToken, address indexed creator, bytes32 indexed orderId, uint256 price, uint256 amount, uint256 numTokensEscrowed, uint256 numSharesEscrowed, bytes32 tradeGroupId);
    event OrderFilled(address indexed shareToken, address indexed creator, address indexed filler, uint256 price, uint256 numCreatorShares, uint256 numCreatorTokens, uint256 numFillerShares, uint256 numFillerTokens, uint256 settlementFees, bytes32 tradeGroupId);
    event ProceedsClaimed(address indexed sender, address indexed market, uint256 numShares, uint256 numPayoutTokens, uint256 finalTokenBalance);

    IUniverse private parentUniverse;
    bytes32 private parentPayoutDistributionHash;
    IReputationToken private reputationToken;
    IMarket private forkingMarket;
    uint256 private forkEndTime;
    mapping(uint256 => IReportingWindow) private reportingWindows;
    mapping(bytes32 => IUniverse) private childUniverses;
    uint256 private openInterestInAttoEth;
    uint256 private extraDisputeBondRemainingToBePaidOut;
    // We increase and decrease this value seperate from the totalSupply as we do not want to count potentional infalitonary bonuses from the migration reward
    uint256 private repAvailableForExtraBondPayouts;

    mapping (address => uint256) private validityBondInAttoeth;
    mapping (address => uint256) private targetReporterGasCosts;
    mapping (address => uint256) private designatedReportStakeInAttoRep;
    mapping (address => uint256) private designatedReportNoShowBondInAttoRep;
    mapping (address => uint256) private shareSettlementFeeDivisor;

    function initialize(IUniverse _parentUniverse, bytes32 _parentPayoutDistributionHash) external beforeInitialized returns (bool) {
        endInitialization();
        parentUniverse = _parentUniverse;
        parentPayoutDistributionHash = _parentPayoutDistributionHash;
        reputationToken = ReputationTokenFactory(controller.lookup("ReputationTokenFactory")).createReputationToken(controller, this);
        require(reputationToken != address(0));
        return true;
    }

    function fork() public afterInitialized returns (bool) {
        require(forkingMarket == address(0));
        require(isContainerForMarket(IMarket(msg.sender)));
        forkingMarket = IMarket(msg.sender);
        forkEndTime = block.timestamp + Reporting.forkDurationSeconds();
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
        return Reporting.reportingDurationSeconds() + Reporting.reportingDisputeDurationSeconds();
    }

    function getReportingWindowByTimestamp(uint256 _timestamp) public returns (IReportingWindow) {
        uint256 _windowId = getReportingWindowId(_timestamp);
        if (reportingWindows[_windowId] == address(0)) {
            reportingWindows[_windowId] = ReportingWindowFactory(controller.lookup("ReportingWindowFactory")).createReportingWindow(controller, this, _windowId);
        }
        return reportingWindows[_windowId];
    }

    function getReportingWindowByMarketEndTime(uint256 _endTime) public returns (IReportingWindow) {
        return getReportingWindowByTimestamp(_endTime + Reporting.designatedReportingDurationSeconds() + Reporting.designatedReportingDisputeDurationSeconds() + 1 + getReportingPeriodDurationInSeconds());
    }

    function getPreviousReportingWindow() public returns (IReportingWindow) {
        return getReportingWindowByTimestamp(block.timestamp - getReportingPeriodDurationInSeconds());
    }

    function getCurrentReportingWindow() public returns (IReportingWindow) {
        return getReportingWindowByTimestamp(block.timestamp);
    }

    function getNextReportingWindow() public returns (IReportingWindow) {
        return getReportingWindowByTimestamp(block.timestamp + getReportingPeriodDurationInSeconds());
    }

    function getOrCreateChildUniverse(bytes32 _parentPayoutDistributionHash) public returns (IUniverse) {
        if (childUniverses[_parentPayoutDistributionHash] == address(0)) {
            childUniverses[_parentPayoutDistributionHash] = UniverseFactory(controller.lookup("UniverseFactory")).createUniverse(controller, this, _parentPayoutDistributionHash);
        }
        return childUniverses[_parentPayoutDistributionHash];
    }

    function getRepAvailableForExtraBondPayouts() public view returns (uint256) {
        return repAvailableForExtraBondPayouts;
    }

    function increaseRepAvailableForExtraBondPayouts(uint256 _amount) public returns (bool) {
        require(msg.sender == address(reputationToken));
        repAvailableForExtraBondPayouts = repAvailableForExtraBondPayouts.add(_amount);
        return true;
    }

    function decreaseRepAvailableForExtraBondPayouts(uint256 _amount) public returns (bool) {
        require(parentUniverse.isContainerForDisputeBondToken(IDisputeBond(msg.sender)));
        repAvailableForExtraBondPayouts = repAvailableForExtraBondPayouts.sub(_amount);
        return true;
    }

    function getExtraDisputeBondRemainingToBePaidOut() public view returns (uint256) {
        return extraDisputeBondRemainingToBePaidOut;
    }

    function increaseExtraDisputeBondRemainingToBePaidOut(uint256 _amount) public returns (bool) {
        require(isContainerForMarket(IMarket(msg.sender)));
        extraDisputeBondRemainingToBePaidOut = extraDisputeBondRemainingToBePaidOut.add(_amount);
        return true;
    }

    function decreaseExtraDisputeBondRemainingToBePaidOut(uint256 _amount) public returns (bool) {
        require(isContainerForDisputeBondToken(IDisputeBond(msg.sender)));
        extraDisputeBondRemainingToBePaidOut = extraDisputeBondRemainingToBePaidOut.sub(_amount);
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

    function isContainerForDisputeBondToken(IDisputeBond _shadyDisputeBond) public view returns (bool) {
        IMarket _shadyMarket = _shadyDisputeBond.getMarket();
        if (_shadyMarket == address(0)) {
            return false;
        }
        if (!isContainerForMarket(_shadyMarket)) {
            return false;
        }
        IMarket _legitMarket = _shadyMarket;
        return _legitMarket.isContainerForDisputeBondToken(_shadyDisputeBond);
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

    function getReportingWindowForForkEndTime() public returns (IReportingWindow) {
        return getReportingWindowByTimestamp(getForkEndTime());
    }

    function decrementOpenInterest(uint256 _amount) public onlyWhitelistedCallers returns (bool) {
        openInterestInAttoEth = openInterestInAttoEth.sub(_amount);
    }

    // CONSIDER: It would be more correct to decrease open interest for all outstanding shares in a market when it is finalized. We aren't doing this currently since securely and correctly writing this code would require updating the Market contract, which is currently at its size limit.
    function incrementOpenInterest(uint256 _amount) public onlyWhitelistedCallers returns (bool) {
        openInterestInAttoEth = openInterestInAttoEth.add(_amount);
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
        return getOpenInterestInAttoEth() * Reporting.targetRepMarketCapMultiplier();
    }

    function getValidityBond() public returns (uint256) {
        IReportingWindow _reportingWindow = getCurrentReportingWindow();
        uint256 _currentValidityBondInAttoeth = validityBondInAttoeth[_reportingWindow];
        if (_currentValidityBondInAttoeth != 0) {
            return _currentValidityBondInAttoeth;
        }
        IReportingWindow _previousReportingWindow = getPreviousReportingWindow();
        uint256 _totalMarketsInPreviousWindow = _previousReportingWindow.getNumMarkets();
        uint256 _invalidMarketsInPreviousWindow = _previousReportingWindow.getNumInvalidMarkets();
        uint256 _previousValidityBondInAttoeth = validityBondInAttoeth[_previousReportingWindow];
        _currentValidityBondInAttoeth = calculateFloatingValue(_invalidMarketsInPreviousWindow, _totalMarketsInPreviousWindow, Reporting.targetInvalidMarketsDivisor(), _previousValidityBondInAttoeth, Reporting.defaultValidityBond(), Reporting.defaultValidityBondFloor());
        validityBondInAttoeth[_reportingWindow] = _currentValidityBondInAttoeth;
        return _currentValidityBondInAttoeth;
    }

    function getDesignatedReportStake() public returns (uint256) {
        IReportingWindow _reportingWindow = getCurrentReportingWindow();
        uint256 _currentDesignatedReportStakeInAttoRep = designatedReportStakeInAttoRep[_reportingWindow];
        if (_currentDesignatedReportStakeInAttoRep != 0) {
            return _currentDesignatedReportStakeInAttoRep;
        }
        IReportingWindow _previousReportingWindow = getPreviousReportingWindow();
        uint256 _totalMarketsInPreviousWindow = _previousReportingWindow.getNumMarkets();
        uint256 _incorrectDesignatedReportMarketsInPreviousWindow = _previousReportingWindow.getNumIncorrectDesignatedReportMarkets();
        uint256 _previousDesignatedReportStakeInAttoRep = designatedReportStakeInAttoRep[_previousReportingWindow];

        _currentDesignatedReportStakeInAttoRep = calculateFloatingValue(_incorrectDesignatedReportMarketsInPreviousWindow, _totalMarketsInPreviousWindow, Reporting.targetIncorrectDesignatedReportMarketsDivisor(), _previousDesignatedReportStakeInAttoRep, Reporting.defaultDesignatedReportStake(), Reporting.designatedReportStakeFloor());
        designatedReportStakeInAttoRep[_reportingWindow] = _currentDesignatedReportStakeInAttoRep;
        return _currentDesignatedReportStakeInAttoRep;
    }

    function getDesignatedReportNoShowBond() public returns (uint256) {
        IReportingWindow _reportingWindow = getCurrentReportingWindow();
        uint256 _currentDesignatedReportNoShowBondInAttoRep = designatedReportNoShowBondInAttoRep[_reportingWindow];
        if (_currentDesignatedReportNoShowBondInAttoRep != 0) {
            return _currentDesignatedReportNoShowBondInAttoRep;
        }
        IReportingWindow _previousReportingWindow = getPreviousReportingWindow();
        uint256 _totalMarketsInPreviousWindow = _previousReportingWindow.getNumMarkets();
        uint256 _designatedReportNoShowsInPreviousWindow = _previousReportingWindow.getNumDesignatedReportNoShows();
        uint256 _previousDesignatedReportNoShowBondInAttoRep = designatedReportStakeInAttoRep[_previousReportingWindow];

        _currentDesignatedReportNoShowBondInAttoRep = calculateFloatingValue(_designatedReportNoShowsInPreviousWindow, _totalMarketsInPreviousWindow, Reporting.targetDesignatedReportNoShowsDivisor(), _previousDesignatedReportNoShowBondInAttoRep, Reporting.defaultDesignatedReportNoShowBond(), Reporting.designatedReportNoShowBondFloor());
        designatedReportStakeInAttoRep[_reportingWindow] = _currentDesignatedReportNoShowBondInAttoRep;
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
            _newValue = _badMarkets.mul(_previousValue).mul(_targetDivisor).div(_totalMarkets).div(2) + _previousValue / 2; // FIXME: This is on one line due to solium bugs
        } else {
            // FXP formula: previous_amount * (1/(1 - target_percent)) * (actual_percent - target_percent) + 1;
            _newValue = _targetDivisor.mul(_previousValue.mul(_badMarkets).div(_totalMarkets).sub(_previousValue.div(_targetDivisor))).div(_targetDivisor - 1) + _previousValue; // FIXME: This is on one line due to a solium bug
        }

        if (_newValue < _floor) {
            _newValue = _floor;
        }

        return _newValue;
    }

    function getReportingFeeDivisor() public returns (uint256) {
        IReportingWindow _reportingWindow = getCurrentReportingWindow();
        uint256 _currentFeeDivisor = shareSettlementFeeDivisor[_reportingWindow];
        if (_currentFeeDivisor != 0) {
            return _currentFeeDivisor;
        }
        uint256 _repMarketCapInAttoeth = getRepMarketCapInAttoeth();
        uint256 _targetRepMarketCapInAttoeth = getTargetRepMarketCapInAttoeth();
        uint256 _previousFeeDivisor = shareSettlementFeeDivisor[getPreviousReportingWindow()];
        if (_previousFeeDivisor == 0) {
            _previousFeeDivisor = 100;
        }
        if (_targetRepMarketCapInAttoeth == 0) {
            _currentFeeDivisor = 10000;
        } else {
            _currentFeeDivisor = _previousFeeDivisor * _repMarketCapInAttoeth / _targetRepMarketCapInAttoeth;
        }
        if (_currentFeeDivisor > 10000) {
            _currentFeeDivisor = 10000;
        }
        shareSettlementFeeDivisor[_reportingWindow] = _currentFeeDivisor;
        return _currentFeeDivisor;
    }

    function getTargetReporterGasCosts() public returns (uint256) {
        IReportingWindow _reportingWindow = getCurrentReportingWindow();
        uint256 _gasToReport = targetReporterGasCosts[_reportingWindow];
        if (_gasToReport != 0) {
            return _gasToReport;
        }

        IReportingWindow _previousReportingWindow = getPreviousReportingWindow();
        uint256 _avgGasPrice = _previousReportingWindow.getAvgReportingGasPrice();
        _gasToReport = Reporting.gasToReport();
        // we double it to try and ensure we have more than enough rather than not enough
        targetReporterGasCosts[_reportingWindow] = _gasToReport * _avgGasPrice * 2;
        return targetReporterGasCosts[_reportingWindow];
    }

    function getMarketCreationCost() public returns (uint256) {
        return getValidityBond() + getTargetReporterGasCosts();
    }

    //
    // Logging
    //

    function logTokensTransferred(address _token, address _from, address _to, uint256 _value) public returns (bool) {
        // VALIDATION
        TokensTransferred(_token, _from, _to, _value);
        return true;
    }

    function logMarketCreated(address _market, address _marketCreator, uint256 _marketCreationFee, string _extraInfo) public returns (bool) {
        require(isContainerForReportingWindow(IReportingWindow(msg.sender)));
        MarketCreated(_market, _marketCreator, _marketCreationFee, _extraInfo);
        return true;
    }

    function logDesignatedReportSubmitted(address _reporter, address _market, address _stakeToken, uint256 _amountStaked, uint256[] _payoutNumerators) public returns (bool) {
        require(isContainerForStakeToken(IStakeToken(msg.sender)));
        DesignatedReportSubmitted(_reporter, _market, _stakeToken, _amountStaked, _payoutNumerators);
        return true;
    }

    function logReportSubmitted(address _reporter, address _market, address _stakeToken, uint256 _amountStaked, uint256[] _payoutNumerators) public returns (bool) {
        require(isContainerForStakeToken(IStakeToken(msg.sender)));
        ReportSubmitted(_reporter, _market, _stakeToken, _amountStaked, _payoutNumerators);
        return true;
    }

    function logWinningTokensRedeemed(address _reporter, address _market, address _stakeToken, uint256 _amountRedeemed, uint256 _reportingFeesReceived, uint256[] _payoutNumerators) public returns (bool) {
        require(isContainerForStakeToken(IStakeToken(msg.sender)));
        WinningTokensRedeemed(_reporter, _market, _stakeToken, _amountRedeemed, _reportingFeesReceived, _payoutNumerators);
        return true;
    }

    function logReportsDisputed(address _disputer, address _market, uint8 _reportingPhase, uint256 _disputeBondAmount) public returns (bool) {
        require(isContainerForMarket(IMarket(msg.sender)));
        ReportsDisputed(_disputer, _market, _reportingPhase, _disputeBondAmount);
        return true;
    }

    function logMarketFinalized(address _market) public returns (bool) {
        // VALIDATION
        MarketFinalized(_market);
        return true;
    }

    function logUniverseForked(address _universe) public returns (bool) {
        // VALIDATION
        UniverseForked(_universe);
        return true;
    }

    function logOrderCanceled(address _shareToken, address _sender, bytes32 _orderId, uint8 _orderType, uint256 _tokenRefund, uint256 _sharesRefund) public returns (bool) {
        // VALIDATION
        OrderCanceled(_shareToken, _sender, _orderId, _orderType, _tokenRefund, _sharesRefund);
        return true;
    }

    function logOrderCreated(address _shareToken, address _creator, bytes32 _orderId, uint256 _price, uint256 _amount, uint256 _numTokensEscrowed, uint256 _numSharesEscrowed, bytes32 _tradeGroupId) public returns (bool) {
        // VALIDATION
        OrderCreated(_shareToken, _creator, _orderId, _price, _amount, _numTokensEscrowed, _numSharesEscrowed, _tradeGroupId);
        return true;
    }

    function logOrderFilled(address _shareToken, address _creator, address _filler, uint256 _price, uint256 _numCreatorShares, uint256 _numCreatorTokens, uint256 _numFillerShares, uint256 _numFillerTokens, uint256 _settlementFees, bytes32 _tradeGroupId) public returns (bool) {
        // VALIDATION
        OrderFilled(_shareToken, _creator, _filler, _price, _numCreatorShares, _numCreatorTokens, _numFillerShares, _numFillerTokens, _settlementFees, _tradeGroupId);
        return true;
    }

    function logProceedsClaimed(address _sender, address _market, uint256 _numShares, uint256 _numPayoutTokens, uint256 _finalTokenBalance) public returns (bool) {
        // VALIDATION
        ProceedsClaimed(_sender, _market, _numShares, _numPayoutTokens, _finalTokenBalance);
        return true;
    }
}
