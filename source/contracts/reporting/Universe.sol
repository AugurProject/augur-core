pragma solidity 0.4.17;


import 'reporting/IUniverse.sol';
import 'libraries/DelegationTarget.sol';
import 'libraries/Typed.sol';
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
import 'libraries/math/SafeMathUint256.sol';


contract Universe is DelegationTarget, Typed, Initializable, IUniverse {
    using SafeMathUint256 for uint256;

    IUniverse private parentUniverse;
    bytes32 private parentPayoutDistributionHash;
    IReputationToken private reputationToken;
    IMarket private forkingMarket;
    uint256 private forkEndTime;
    mapping(uint256 => IReportingWindow) private reportingWindows;
    mapping(bytes32 => IUniverse) private childUniverses;
    uint256 private openInterestInAttoEth;

    mapping (address => uint256) private validityBondInAttoeth;
    mapping (address => uint256) private targetReporterGasCosts;
    mapping (address => uint256) private designatedReportStakeInAttoRep;
    mapping (address => uint256) private designatedReportNoShowBondInAttoRep;
    mapping (address => uint256) private shareSettlementPerEthFee;

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
        require(isContainerForMarket(Typed(msg.sender)));
        forkingMarket = IMarket(msg.sender);
        forkEndTime = block.timestamp + 60 days;
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

    function isContainerForReportingWindow(Typed _shadyTarget) public view returns (bool) {
        if (_shadyTarget.getTypeName() != "ReportingWindow") {
            return false;
        }
        IReportingWindow _shadyReportingWindow = IReportingWindow(_shadyTarget);
        uint256 _startTime = _shadyReportingWindow.getStartTime();
        if (_startTime == 0) {
            return false;
        }
        uint256 _reportingWindowId = getReportingWindowId(_startTime);
        IReportingWindow _legitReportingWindow = reportingWindows[_reportingWindowId];
        return _shadyReportingWindow == _legitReportingWindow;
    }

    function isContainerForDisputeBondToken(Typed _shadyTarget) public view returns (bool) {
        if (_shadyTarget.getTypeName() != "DisputeBondToken") {
            return false;
        }
        IDisputeBond _shadyDisputeBond = IDisputeBond(_shadyTarget);
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

    function isContainerForMarket(Typed _shadyTarget) public view returns (bool) {
        if (_shadyTarget.getTypeName() != "Market") {
            return false;
        }
        IMarket _shadyMarket = IMarket(_shadyTarget);
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

    function isContainerForStakeToken(Typed _shadyTarget) public view returns (bool) {
        if (_shadyTarget.getTypeName() != "StakeToken") {
            return false;
        }
        IStakeToken _shadyStakeToken = IStakeToken(_shadyTarget);
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

    function isContainerForShareToken(Typed _shadyTarget) public view returns (bool) {
        if (_shadyTarget.getTypeName() != "ShareToken") {
            return false;
        }
        IShareToken _shadyShareToken = IShareToken(_shadyTarget);
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
        // TODO: get this from a multi-sig contract that we provide and maintain
        uint256 _attorepPerEth = 11 * 10 ** 18;
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
            _newValue = _badMarkets.mul(_previousValue).mul(_targetDivisor).div(_totalMarkets).div(2)  + _previousValue / 2; // FIXME: This is on one line due to solium bugs
        } else {
            // FXP formula: previous_amount * (1/(1 - target_percent)) * (actual_percent - target_percent) + 1;
            _newValue = _targetDivisor.mul(_previousValue.mul(_badMarkets).div(_totalMarkets).sub(_previousValue.div(_targetDivisor))).div(_targetDivisor - 1) + _previousValue; // FIXME: This is on one line due to a solium bug
        }

        if (_newValue < _floor) {
            _newValue = _floor;
        }

        return _newValue;
    }

    function getReportingFeeInAttoethPerEth() public returns (uint256) {
        IReportingWindow _reportingWindow = getCurrentReportingWindow();
        uint256 _currentPerEthFee = shareSettlementPerEthFee[_reportingWindow];
        if (_currentPerEthFee != 0) {
            return _currentPerEthFee;
        }
        uint256 _repMarketCapInAttoeth = getRepMarketCapInAttoeth();
        uint256 _targetRepMarketCapInAttoeth = getTargetRepMarketCapInAttoeth();
        uint256 _previousPerEthFee = shareSettlementPerEthFee[getPreviousReportingWindow()];
        if (_previousPerEthFee == 0) {
            _previousPerEthFee = 1 * 10 ** 16;
        }
        _currentPerEthFee = _previousPerEthFee * _targetRepMarketCapInAttoeth / _repMarketCapInAttoeth;
        if (_currentPerEthFee < 1 * 10 ** 14) {
            _currentPerEthFee = 1 * 10 ** 14;
        }
        shareSettlementPerEthFee[_reportingWindow] = _currentPerEthFee;
        return _currentPerEthFee;
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
}
