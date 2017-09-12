pragma solidity ^0.4.13;

import 'ROOT/reporting/IReportingToken.sol';
import 'ROOT/libraries/DelegationTarget.sol';
import 'ROOT/libraries/Typed.sol';
import 'ROOT/libraries/Initializable.sol';
import 'ROOT/libraries/token/VariableSupplyToken.sol';
import 'ROOT/reporting/IBranch.sol';
import 'ROOT/reporting/IReputationToken.sol';
import 'ROOT/reporting/IReportingToken.sol';
import 'ROOT/reporting/IDisputeBond.sol';
import 'ROOT/reporting/IRegistrationToken.sol';
import 'ROOT/reporting/IReportingWindow.sol';
import 'ROOT/reporting/IMarket.sol';
import 'ROOT/libraries/math/SafeMathUint256.sol';


contract ReportingToken is DelegationTarget, Typed, Initializable, VariableSupplyToken, IReportingToken {
    using SafeMathUint256 for uint256;

    IMarket public market;
    uint256[] public payoutNumerators;

    function initialize(IMarket _market, uint256[] _payoutNumerators) public beforeInitialized returns (bool) {
        endInitialization();
        require(_market.getNumberOfOutcomes() == _payoutNumerators.length);
        market = _market;
        payoutNumerators = _payoutNumerators;
        // TODO: call a function on `self.getBranch()` that logs the creation of this token with an index for the market, function needs to verify that caller is `branch.isContainerForReportingToken(thisToken)`
        return true;
    }

    function buy(uint256 _attotokens) public afterInitialized returns (bool) {
        IMarket.ReportingState _state = market.getReportingState();
        require(_state == IMarket.ReportingState.LIMITED_REPORTING || _state == IMarket.ReportingState.ALL_REPORTING);
        require(getRegistrationToken().balanceOf(msg.sender) > 0);
        require(market.isContainerForReportingToken(this));
        getReputationToken().trustedTransfer(msg.sender, this, _attotokens);
        mint(msg.sender, _attotokens);
        bytes32 _payoutDistributionHash = getPayoutDistributionHash();
        market.updateTentativeWinningPayoutDistributionHash(_payoutDistributionHash);
        getReportingWindow().noteReport(market, msg.sender, _payoutDistributionHash);
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
        require(getBranch().getForkingMarket() == market);
        var _sourceReputationToken = getReputationToken();
        var _reputationSupply = _sourceReputationToken.balanceOf(this);
        var _attotokens = balances[msg.sender];
        var _reporterReputationShare = _reputationSupply * _attotokens / supply;
        burn(msg.sender, _attotokens);
        var _destinationReputationToken = getBranch().getChildBranch(getPayoutDistributionHash()).getReputationToken();
        _sourceReputationToken.migrateOut(_destinationReputationToken, this, _attotokens);
        _destinationReputationToken.transfer(msg.sender, _reporterReputationShare);
        return true;
    }

    // NOTE: UI should warn users about calling this before first calling `migrateLosingTokens` on all losing tokens with non-dust contents
    function redeemWinningTokens() public afterInitialized returns (bool) {
        require(market.getReportingState() == IMarket.ReportingState.FINALIZED);
        require(market.isContainerForReportingToken(this));
        require(getBranch().getForkingMarket() != market);
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
        require(getBranch().getForkingMarket() != market);
        require(market.getFinalWinningReportingToken() != this);
        migrateLosingTokenRepToDisputeBond(market.getAutomatedReporterDisputeBondToken());
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

    function getTypeName() public constant returns (bytes32) {
        return "ReportingToken";
    }

    function getBranch() public constant returns (IBranch) {
        return market.getBranch();
    }

    function getReputationToken() public constant returns (IReputationToken) {
        return market.getReportingWindow().getReputationToken();
    }

    function getReportingWindow() public constant returns (IReportingWindow) {
        return market.getReportingWindow();
    }

    function getRegistrationToken() public constant returns (IRegistrationToken) {
        return getReportingWindow().getRegistrationToken();
    }

    function getMarket() public constant returns (IMarket) {
        return market;
    }

    function getPayoutDistributionHash() public constant returns (bytes32) {
        return market.derivePayoutDistributionHash(payoutNumerators);
    }

    function getPayoutNumerator(uint8 index) public constant returns (uint256) {
        require(index < market.getNumberOfOutcomes());
        return payoutNumerators[index];
    }
}
