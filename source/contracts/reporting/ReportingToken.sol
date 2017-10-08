pragma solidity 0.4.17;


import 'reporting/IReportingToken.sol';
import 'libraries/DelegationTarget.sol';
import 'libraries/Typed.sol';
import 'libraries/Initializable.sol';
import 'libraries/token/VariableSupplyToken.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReputationToken.sol';
import 'reporting/IReportingToken.sol';
import 'reporting/IDisputeBond.sol';
import 'reporting/IRegistrationToken.sol';
import 'reporting/IReportingWindow.sol';
import 'reporting/IMarket.sol';
import 'libraries/math/SafeMathUint256.sol';
import 'extensions/MarketFeeCalculator.sol';


contract ReportingToken is DelegationTarget, Typed, Initializable, VariableSupplyToken, IReportingToken {
    using SafeMathUint256 for uint256;

    IMarket public market;
    uint256[] public payoutNumerators;

    function initialize(IMarket _market, uint256[] _payoutNumerators) public beforeInitialized returns (bool) {
        endInitialization();
        require(_market.getNumberOfOutcomes() == _payoutNumerators.length);
        market = _market;
        payoutNumerators = _payoutNumerators;
        return true;
    }

    function buy(uint256 _attotokens) public afterInitialized returns (bool) {
        IMarket.ReportingState _state = market.getReportingState();
        if (_state == IMarket.ReportingState.AWAITING_NO_REPORT_MIGRATION) {
            market.migrateDueToNoReports();
            if (getRegistrationToken().balanceOf(msg.sender) == 0) {
                return false;
            }
        } else if (_state == IMarket.ReportingState.DESIGNATED_REPORTING) {
            require(msg.sender == market.getDesignatedReporter());
            uint256 _designatedDisputeCost = MarketFeeCalculator(controller.lookup("MarketFeeCalculator")).getDesignatedReportStake(market.getReportingWindow());
            require(_attotokens == _designatedDisputeCost);
        } else {
            require(_state == IMarket.ReportingState.LIMITED_REPORTING || _state == IMarket.ReportingState.ALL_REPORTING);
        }
        require(getRegistrationToken().balanceOf(msg.sender) > 0);
        require(market.isContainerForReportingToken(this));
        getReputationToken().trustedTransfer(msg.sender, this, _attotokens);
        mint(msg.sender, _attotokens);
        bytes32 _payoutDistributionHash = getPayoutDistributionHash();
        market.updateTentativeWinningPayoutDistributionHash(_payoutDistributionHash);
        getReportingWindow().noteReport(market, msg.sender, _payoutDistributionHash);
        if (_state == IMarket.ReportingState.DESIGNATED_REPORTING) {
            market.designatedReport();
        }
        return true;
    }

    function redeemDisavowedTokens(address _reporter) public afterInitialized returns (bool) {
        require(!market.isContainerForReportingToken(this));
        var _reputationSupply = getReputationToken().balanceOf(this);
        var _attotokens = balances[_reporter];
        var _reporterReputationShare = _reputationSupply * _attotokens / supply;
        burn(_reporter, _attotokens);
        getReputationToken().transfer(_reporter, _reporterReputationShare);
        return true;
    }

    // NOTE: UI should warn users about calling this before first calling `migrateLosingTokens` on all losing tokens with non-dust contents
    function redeemForkedTokens() public afterInitialized returns (bool) {
        require(market.isContainerForReportingToken(this));
        require(getUniverse().getForkingMarket() == market);
        var _sourceReputationToken = getReputationToken();
        var _reputationSupply = _sourceReputationToken.balanceOf(this);
        var _attotokens = balances[msg.sender];
        var _reporterReputationShare = _reputationSupply * _attotokens / supply;
        burn(msg.sender, _attotokens);
        var _destinationReputationToken = getUniverse().getOrCreateChildUniverse(getPayoutDistributionHash()).getReputationToken();
        _sourceReputationToken.migrateOut(_destinationReputationToken, this, _attotokens);
        _destinationReputationToken.transfer(msg.sender, _reporterReputationShare);
        return true;
    }

    // NOTE: UI should warn users about calling this before first calling `migrateLosingTokens` on all losing tokens with non-dust contents
    // TODO: prevent calling this until all markets on the reporting window are finalized.
    // TODO: add reporting fee distribution to this.
    function redeemWinningTokens() public afterInitialized returns (bool) {
        require(market.getReportingState() == IMarket.ReportingState.FINALIZED);
        require(market.isContainerForReportingToken(this));
        require(getUniverse().getForkingMarket() != market);
        require(market.getFinalWinningReportingToken() == this);
        var _reputationToken = getReputationToken();
        var _reputationSupply = _reputationToken.balanceOf(this);
        var _attotokens = balances[msg.sender];
        var _reporterReputationShare = _reputationSupply * _attotokens / supply;
        burn(msg.sender, _attotokens);
        if (_reporterReputationShare == 0) {
            return true;
        }
        _reputationToken.transfer(msg.sender, _reporterReputationShare);
        return true;
    }

    function migrateLosingTokens() public afterInitialized returns (bool) {
        require(market.getReportingState() == IMarket.ReportingState.FINALIZED);
        require(market.isContainerForReportingToken(this));
        require(getUniverse().getForkingMarket() != market);
        require(market.getFinalWinningReportingToken() != this);
        migrateLosingTokenRepToDisputeBond(market.getDesignatedReporterDisputeBondToken());
        migrateLosingTokenRepToDisputeBond(market.getLimitedReportersDisputeBondToken());
        migrateLosingTokenRepToWinningToken();
        return true;
    }

    function migrateLosingTokenRepToDisputeBond(IDisputeBond _disputeBondToken) private returns (bool) {
        if (_disputeBondToken == address(0)) {
            return true;
        }
        if (_disputeBondToken.getDisputedPayoutDistributionHash() == market.getFinalPayoutDistributionHash()) {
            return true;
        }
        var _reputationToken = getReputationToken();
        var _amountNeeded = _disputeBondToken.getBondRemainingToBePaidOut() - _reputationToken.balanceOf(_disputeBondToken);
        var _amountToTransfer = _amountNeeded.min(_reputationToken.balanceOf(this));
        if (_amountToTransfer == 0) {
            return true;
        }
        _reputationToken.transfer(_disputeBondToken, _amountToTransfer);
        return true;
    }

    function migrateLosingTokenRepToWinningToken() private returns (bool) {
        var _reputationToken = getReputationToken();
        var _balance = _reputationToken.balanceOf(this);
        if (_balance == 0) {
            return true;
        }
        _reputationToken.transfer(market.getFinalWinningReportingToken(), _balance);
        return true;
    }

    function getTypeName() public view returns (bytes32) {
        return "ReportingToken";
    }

    function getUniverse() public view returns (IUniverse) {
        return market.getUniverse();
    }

    function getReputationToken() public view returns (IReputationToken) {
        return market.getReportingWindow().getReputationToken();
    }

    function getReportingWindow() public view returns (IReportingWindow) {
        return market.getReportingWindow();
    }

    function getRegistrationToken() public view returns (IRegistrationToken) {
        return getReportingWindow().getRegistrationToken();
    }

    function getMarket() public view returns (IMarket) {
        return market;
    }

    function getPayoutDistributionHash() public view returns (bytes32) {
        return market.derivePayoutDistributionHash(payoutNumerators);
    }

    function getPayoutNumerator(uint8 index) public view returns (uint256) {
        require(index < market.getNumberOfOutcomes());
        return payoutNumerators[index];
    }

    function isValid() public view returns (bool) {
        for (uint8 i = 1; i < payoutNumerators.length; i++) {
            if (payoutNumerators[0] != payoutNumerators[i]) {
                return true;
            }
        }
        return false;
    }
}
