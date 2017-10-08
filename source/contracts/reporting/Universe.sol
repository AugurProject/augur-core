pragma solidity 0.4.17;
pragma experimental ABIEncoderV2;
pragma experimental "v0.5.0";

import 'reporting/IUniverse.sol';
import 'libraries/DelegationTarget.sol';
import 'libraries/Typed.sol';
import 'libraries/Initializable.sol';
import 'factories/ReputationTokenFactory.sol';
import 'factories/ReportingWindowFactory.sol';
import 'factories/UniverseFactory.sol';
import 'reporting/IMarket.sol';
import 'reporting/IReputationToken.sol';
import 'reporting/IReportingToken.sol';
import 'reporting/IDisputeBond.sol';
import 'reporting/IRegistrationToken.sol';
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

    function getTypeName() public constant returns (bytes32) {
        return "Universe";
    }

    function getParentUniverse() public constant returns (IUniverse) {
        return parentUniverse;
    }

    function getParentPayoutDistributionHash() public constant returns (bytes32) {
        return parentPayoutDistributionHash;
    }

    function getReputationToken() public constant returns (IReputationToken) {
        return reputationToken;
    }

    function getForkingMarket() public constant returns (IMarket) {
        return forkingMarket;
    }

    function getForkEndTime() public constant returns (uint256) {
        return forkEndTime;
    }

    function getReportingWindow(uint256 _reportingWindowId) public constant returns (IReportingWindow) {
        return reportingWindows[_reportingWindowId];
    }

    function getChildUniverse(bytes32 _parentPayoutDistributionHash) public constant returns (IUniverse) {
        return childUniverses[_parentPayoutDistributionHash];
    }

    function getReportingWindowId(uint256 _timestamp) public constant returns (uint256) {
        return _timestamp / getReportingPeriodDurationInSeconds();
    }

    function getReportingPeriodDurationInSeconds() public constant returns (uint256) {
        return Reporting.reportingDurationSeconds() + Reporting.reportingDisputeDurationSeconds();
    }

    function getReportingWindowByTimestamp(uint256 _timestamp) public returns (IReportingWindow) {
        uint256 _windowId = getReportingWindowId(_timestamp);
        if (reportingWindows[_windowId] == address(0)) {
            reportingWindows[_windowId] = ReportingWindowFactory(controller.lookup("ReportingWindowFactory")).createReportingWindow(controller, this, _windowId);
        }
        return reportingWindows[_windowId];
    }

    function getReportingWindowByMarketEndTime(uint256 _endTime, bool _hasDesignatedReporter) public returns (IReportingWindow) {
        if (_hasDesignatedReporter) {
            return getReportingWindowByTimestamp(_endTime + Reporting.designatedReportingDurationSeconds() + Reporting.designatedReportingDisputeDurationSeconds() + 1 + getReportingPeriodDurationInSeconds());
        } else {
            return getReportingWindowByTimestamp(_endTime + 1 + getReportingPeriodDurationInSeconds());
        }
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

    function isContainerForReportingWindow(Typed _shadyTarget) public constant returns (bool) {
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

    function isContainerForDisputeBondToken(Typed _shadyTarget) public returns (bool) {
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

    function isContainerForRegistrationToken(Typed _shadyTarget) public constant returns (bool) {
        if (_shadyTarget.getTypeName() != "RegistrationToken") {
            return false;
        }
        IRegistrationToken _shadyRegistrationToken = IRegistrationToken(_shadyTarget);
        IReportingWindow _shadyReportingWindow = _shadyRegistrationToken.getReportingWindow();
        if (_shadyReportingWindow == address(0)) {
            return false;
        }
        if (!isContainerForReportingWindow(_shadyReportingWindow)) {
            return false;
        }
        IReportingWindow _legitReportingWindow = _shadyReportingWindow;
        return _legitReportingWindow.isContainerForRegistrationToken(_shadyRegistrationToken);
    }

    function isContainerForMarket(Typed _shadyTarget) public returns (bool) {
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

    function isContainerForReportingToken(Typed _shadyTarget) public returns (bool) {
        if (_shadyTarget.getTypeName() != "ReportingToken") {
            return false;
        }
        IReportingToken _shadyReportingToken = IReportingToken(_shadyTarget);
        IMarket _shadyMarket = _shadyReportingToken.getMarket();
        if (_shadyMarket == address(0)) {
            return false;
        }
        if (!isContainerForMarket(_shadyMarket)) {
            return false;
        }
        IMarket _legitMarket = _shadyMarket;
        return _legitMarket.isContainerForReportingToken(_shadyReportingToken);
    }

    function isContainerForShareToken(Typed _shadyTarget) public returns (bool) {
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

    function isParentOf(IUniverse _shadyChild) public constant returns (bool) {
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

    function getOpenInterestInAttoEth() public constant returns (uint256) {
        return openInterestInAttoEth;
    }
}
