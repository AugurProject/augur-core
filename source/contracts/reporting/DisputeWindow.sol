// Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE

pragma solidity 0.4.24;


import 'reporting/IDisputeWindow.sol';
import 'Controlled.sol';
import 'libraries/Initializable.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReputationToken.sol';
import 'reporting/IMarket.sol';
import 'trading/ICash.sol';
import 'factories/MarketFactory.sol';
import 'reporting/Reporting.sol';
import 'libraries/math/SafeMathUint256.sol';
import 'reporting/IDisputeWindow.sol';


contract DisputeWindow is Controlled, Initializable, IDisputeWindow {
    using SafeMathUint256 for uint256;

    IUniverse private universe;
    uint256 private startTime;
    uint256 private numMarkets;
    uint256 private invalidMarketsCount;
    uint256 private incorrectDesignatedReportMarketCount;
    uint256 private designatedReportNoShows;

    function initialize(IUniverse _universe, uint256 _disputeWindowId) public beforeInitialized returns (bool) {
        endInitialization();
        universe = _universe;
        startTime = _disputeWindowId.mul(universe.getDisputeRoundDurationInSeconds());
        return true;
    }

    function onMarketFinalized() public afterInitialized returns (bool) {
        IMarket _market = IMarket(msg.sender);
        require(universe.isContainerForMarket(_market));
        numMarkets += 1;
        if (_market.isInvalid()) {
            invalidMarketsCount += 1;
        }
        if (!_market.designatedReporterWasCorrect()) {
            incorrectDesignatedReportMarketCount += 1;
        }
        if (!_market.designatedReporterShowed()) {
            designatedReportNoShows += 1;
        }
        return true;
    }

    function getTypeName() public afterInitialized view returns (bytes32) {
        return "DisputeWindow";
    }

    function getUniverse() public afterInitialized view returns (IUniverse) {
        return universe;
    }

    function getNumMarkets() public afterInitialized view returns (uint256) {
        return numMarkets;
    }

    function getReputationToken() public afterInitialized view returns (IReputationToken) {
        return universe.getReputationToken();
    }

    function getStartTime() public afterInitialized view returns (uint256) {
        return startTime;
    }

    function getEndTime() public afterInitialized view returns (uint256) {
        return getStartTime().add(Reporting.getDisputeRoundDurationSeconds());
    }

    function getNumInvalidMarkets() public afterInitialized view returns (uint256) {
        return invalidMarketsCount;
    }

    function getNumIncorrectDesignatedReportMarkets() public view returns (uint256) {
        return incorrectDesignatedReportMarketCount;
    }

    function getNumDesignatedReportNoShows() public view returns (uint256) {
        return designatedReportNoShows;
    }

    function isActive() public afterInitialized view returns (bool) {
        if (controller.getTimestamp() <= getStartTime()) {
            return false;
        }
        if (controller.getTimestamp() >= getEndTime()) {
            return false;
        }
        return true;
    }

    function isOver() public afterInitialized view returns (bool) {
        return controller.getTimestamp() >= getEndTime();
    }
}
