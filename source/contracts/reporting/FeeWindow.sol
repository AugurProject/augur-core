// Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE

pragma solidity 0.4.20;


import 'reporting/IFeeWindow.sol';
import 'libraries/DelegationTarget.sol';
import 'libraries/Initializable.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReputationToken.sol';
import 'reporting/IMarket.sol';
import 'trading/ICash.sol';
import 'factories/MarketFactory.sol';
import 'reporting/Reporting.sol';
import 'libraries/math/SafeMathUint256.sol';
import 'libraries/math/RunningAverage.sol';
import 'reporting/IFeeWindow.sol';
import 'libraries/token/VariableSupplyToken.sol';
import 'reporting/IFeeToken.sol';
import 'factories/FeeTokenFactory.sol';


contract FeeWindow is DelegationTarget, VariableSupplyToken, Initializable, IFeeWindow {
    using SafeMathUint256 for uint256;
    using RunningAverage for RunningAverage.Data;

    string constant public name = "Participation Token";
    string constant public symbol = "PT";
    uint8 constant public decimals = 0;

    IUniverse private universe;
    uint256 private startTime;
    uint256 private numMarkets;
    uint256 private invalidMarketsCount;
    uint256 private incorrectDesignatedReportMarketCount;
    uint256 private designatedReportNoShows;
    RunningAverage.Data private reportingGasPrice;
    uint256 private totalWinningStake;
    uint256 private totalStake;
    IFeeToken private feeToken;

    function initialize(IUniverse _universe, uint256 _feeWindowId) public onlyInGoodTimes beforeInitialized returns (bool) {
        endInitialization();
        universe = _universe;
        startTime = _feeWindowId.mul(universe.getDisputeRoundDurationInSeconds());
        // Initialize this to some reasonable value to handle the first market ever created without branching code
        reportingGasPrice.record(Reporting.getDefaultReportingGasPrice());
        feeToken = FeeTokenFactory(controller.lookup("FeeTokenFactory")).createFeeToken(controller, this);
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
        buyInternal(msg.sender, _attotokens);
        return true;
    }

    function trustedUniverseBuy(address _buyer, uint256 _attotokens) public onlyInGoodTimes afterInitialized returns (bool) {
        require(IUniverse(msg.sender) == universe);
        buyInternal(_buyer, _attotokens);
        return true;
    }

    function buyInternal(address _buyer, uint256 _attotokens) private onlyInGoodTimes afterInitialized returns (bool) {
        require(_attotokens > 0);
        require(isActive());
        require(!universe.isForking());
        getReputationToken().trustedFeeWindowTransfer(_buyer, this, _attotokens);
        mint(_buyer, _attotokens);
        return true;
    }

    function redeemForReportingParticipant() public returns (bool) {
        redeemInternal(msg.sender, true);
        return true;
    }

    function redeem(address _sender) public returns (bool) {
        redeemInternal(_sender, false);
        return true;
    }

    function redeemInternal(address _sender, bool _isReportingParticipant) private returns (bool) {
        require(isOver() || universe.isForking());

        uint256 _attoParticipationTokens = balances[_sender];
        uint256 _attoFeeTokens = feeToken.balanceOf(_sender);
        uint256 _totalTokens = _attoParticipationTokens.add(_attoFeeTokens);

        uint256 _totalFeeStake = getTotalFeeStake();

        if (_attoParticipationTokens != 0) {
            burn(_sender, _attoParticipationTokens);
            require(getReputationToken().transfer(_sender, _attoParticipationTokens));
        }

        if (_attoFeeTokens != 0) {
            feeToken.feeWindowBurn(_sender, _attoFeeTokens);
        }

        if (_totalFeeStake == 0) {
            return true;
        }

        // CASH
        ICash _cash = ICash(controller.lookup("Cash"));
        uint256 _balance = _cash.balanceOf(this);
        uint256 _feePayoutShare = _balance.mul(_totalTokens).div(_totalFeeStake);

        if (_feePayoutShare > 0) {
            // We can't use the cash.withdrawEtherTo method as the ReportingParticipants are delegated and the fallback function has special behavior that will fail
            if (_isReportingParticipant) {
                require(_cash.transfer(_sender, _feePayoutShare));
            } else {
                _cash.withdrawEtherTo(_sender, _feePayoutShare);
            }
        }
        if (_attoParticipationTokens > 0) {
            controller.getAugur().logFeeWindowRedeemed(universe, _sender, _attoParticipationTokens, _feePayoutShare);
        }
        return true;
    }

    function withdrawInEmergency() public onlyInBadTimes returns (bool) {
        uint256 _attotokens = balances[msg.sender];
        if (_attotokens != 0) {
            burn(msg.sender, _attotokens);
            require(getReputationToken().transfer(msg.sender, _attotokens));
        }
        return true;
    }

    function mintFeeTokens(uint256 _amount) public returns (bool) {
        require(universe.isContainerForReportingParticipant(IReportingParticipant(msg.sender)));
        feeToken.mintForReportingParticipant(msg.sender, _amount);
        return true;
    }

    function getTotalFeeStake() public view returns (uint256) {
        uint256 _totalParticipationSupply = totalSupply();
        uint256 _totalFeeSupply = feeToken.totalSupply();
        return _totalParticipationSupply.add(_totalFeeSupply);
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
        return getStartTime().add(Reporting.getDisputeRoundDurationSeconds());
    }

    function getFeeToken() public afterInitialized view returns (IFeeToken) {
        return feeToken;
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
}
