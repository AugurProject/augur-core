// Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE

pragma solidity 0.4.18;


import 'reporting/IFeeWindow.sol';
import 'libraries/DelegationTarget.sol';
import 'libraries/Initializable.sol';
import 'libraries/collections/Set.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReputationToken.sol';
import 'reporting/IMarket.sol';
import 'trading/ICash.sol';
import 'factories/MarketFactory.sol';
import 'reporting/Reporting.sol';
import 'libraries/math/SafeMathUint256.sol';
import 'libraries/math/RunningAverage.sol';
import 'reporting/IFeeWindow.sol';
import 'factories/FeeWindowFactory.sol';
import 'libraries/Extractable.sol';
import 'libraries/token/VariableSupplyToken.sol';


contract FeeWindow is DelegationTarget, VariableSupplyToken, Extractable, Initializable, IFeeWindow {
    using SafeMathUint256 for uint256;
    using Set for Set.Data;
    using RunningAverage for RunningAverage.Data;

    IUniverse private universe;
    uint256 private startTime;
    uint256 private numMarkets;
    uint256 private invalidMarketsCount;
    uint256 private incorrectDesignatedReportMarketCount;
    uint256 private designatedReportNoShows;
    RunningAverage.Data private reportingGasPrice;
    uint256 private totalWinningStake;
    uint256 private totalStake;

    function initialize(IUniverse _universe, uint256 _feeWindowId) public onlyInGoodTimes beforeInitialized returns (bool) {
        endInitialization();
        universe = _universe;
        startTime = _feeWindowId * universe.getDisputeRoundDurationInSeconds();
        // Initialize this to some reasonable value to handle the first market ever created without branching code
        reportingGasPrice.record(Reporting.getDefaultReportingGasPrice());
        return true;
    }

    function noteInitialReportingGasPrice() public onlyInGoodTimes afterInitialized returns (bool) {
        require(universe.isContainerForReportingParticipant(IReportingParticipant(msg.sender)));
        reportingGasPrice.record(tx.gasprice);
        return true;
    }

    function onMarketFinalized() public onlyInGoodTimes afterInitialized returns (bool) {
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

    function buy(uint256 _attotokens) public onlyInGoodTimes afterInitialized returns (bool) {
        require(_attotokens > 0);
        // The initial reporter can purchase tokens in the window before it is active
        require(isActive() || universe.isContainerForReportingParticipant(IReportingParticipant(msg.sender)));
        getReputationToken().trustedFeeWindowTransfer(msg.sender, this, _attotokens);
        mint(msg.sender, _attotokens);
        return true;
    }

    function redeem(address _sender) public returns (bool) {
        require(isOver());

        uint256 _attotokens = balances[_sender];
        if (_attotokens == 0) {
            return true;
        }
        uint256 _totalSupply = totalSupply();
        burn(_sender, _attotokens);

        // REP
        getReputationToken().transfer(_sender, _attotokens);

        // CASH
        ICash _cash = ICash(controller.lookup("Cash"));
        uint256 _balance = _cash.balanceOf(this);
        uint256 _feePayoutShare = _balance.mul(_attotokens).div(_totalSupply);
        if (_feePayoutShare > 0) {
            _cash.withdrawEtherTo(_sender, _feePayoutShare);
        }
        return true;
    }

    function getAvgReportingGasPrice() public view returns (uint256) {
        return reportingGasPrice.currentAverage();
    }

    function getTypeName() public afterInitialized view returns (bytes32) {
        return "FeeWindow";
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
        return getStartTime() + Reporting.getDisputeRoundDurationSeconds();
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

    function isForkingMarketFinalized() public afterInitialized view returns (bool) {
        return universe.getForkingMarket().isFinalized();
    }

    function onTokenTransfer(address _from, address _to, uint256 _value) internal returns (bool) {
        controller.getAugur().logFeeWindowTransferred(universe, _from, _to, _value);
        return true;
    }

    function onMint(address _target, uint256 _amount) internal returns (bool) {
        controller.getAugur().logFeeWindowMinted(universe, _target, _amount);
        return true;
    }

    function onBurn(address _target, uint256 _amount) internal returns (bool) {
        controller.getAugur().logFeeWindowBurned(universe, _target, _amount);
        return true;
    }

    // Disallow Cash and REP extraction
    function getProtectedTokens() internal returns (address[] memory) {
        address[] memory _protectedTokens = new address[](2);
        _protectedTokens[0] = controller.lookup("Cash");
        _protectedTokens[1] = getReputationToken();
        return _protectedTokens;
    }
}
