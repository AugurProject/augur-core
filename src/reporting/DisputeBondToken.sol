pragma solidity ^0.4.13;

import 'ROOT/reporting/IDisputeBond.sol';
import 'ROOT/libraries/DelegationTarget.sol';
import 'ROOT/libraries/Typed.sol';
import 'ROOT/libraries/Initializable.sol';
import 'ROOT/libraries/token/ERC20Basic.sol';
import 'ROOT/reporting/IBranch.sol';
import 'ROOT/reporting/IReputationToken.sol';
import 'ROOT/reporting/IMarket.sol';
import 'ROOT/libraries/math/SafeMathUint256.sol';


// CONSIDER: This could probably just be made Ownable instead if implementing ERC20Basic
contract DisputeBondToken is DelegationTarget, Typed, Initializable, ERC20Basic, IDisputeBond {
    using SafeMathUint256 for uint256;

    IMarket private market;
    address private bondHolder;
    bytes32 private disputedPayoutDistributionHash;
    uint256 private bondRemainingToBePaidOut;

    function initialize(IMarket _market, address _bondHolder, uint256 _bondAmount, bytes32 _payoutDistributionHash) public beforeInitialized returns (bool) {
        endInitialization();
        market = _market;
        bondHolder = _bondHolder;
        disputedPayoutDistributionHash = _payoutDistributionHash;
        bondRemainingToBePaidOut = _bondAmount * 2;
        return true;
    }

    function withdraw() public returns (bool) {
        require(msg.sender == bondHolder);
        bool _isFinalized = market.getReportingState() == IMarket.ReportingState.FINALIZED;
        require(!market.isContainerForDisputeBondToken(this) || (_isFinalized && market.getFinalPayoutDistributionHash() != disputedPayoutDistributionHash));
        require(getBranch().getForkingMarket() != market);
        IReputationToken _reputationToken = getReputationToken();
        uint256 _amountToTransfer = _reputationToken.balanceOf(this);
        bondRemainingToBePaidOut = bondRemainingToBePaidOut.sub(_amountToTransfer);
        _reputationToken.transfer(bondHolder, _amountToTransfer);
        return true;
    }

    // FIXME: We should be minting coins in this scenario in order to achieve 2x target payout for bond holders during a fork.  Ideally, the amount minted is capped at the amount of tokens redeemed on other branches, so we may have to require the user to supply branches to deduct from with their call to this.
    function withdrawToBranch(IBranch _shadyBranch) public returns (bool) {
        require(msg.sender == bondHolder);
        require(!market.isContainerForDisputeBondToken(this) || getBranch().getForkingMarket() == market);
        bool _isChildOfMarketBranch = market.getReportingWindow().getBranch().isParentOf(_shadyBranch);
        require(_isChildOfMarketBranch);
        IBranch _legitBranch = _shadyBranch;
        require(_legitBranch.getParentPayoutDistributionHash() != disputedPayoutDistributionHash);
        IReputationToken _reputationToken = getReputationToken();
        uint256 _amountToTransfer = _reputationToken.balanceOf(this);
        IReputationToken _destinationReputationToken = _legitBranch.getReputationToken();
        _reputationToken.migrateOut(_destinationReputationToken, this, _amountToTransfer);
        bondRemainingToBePaidOut = bondRemainingToBePaidOut.sub(_amountToTransfer);
        _destinationReputationToken.transfer(bondHolder, _amountToTransfer);
        return true;
    }

    function getTypeName() constant public returns (bytes32) {
        return "DisputeBondToken";
    }

    function getMarket() constant public returns (IMarket) {
        return market;
    }

    function getBranch() constant public returns (IBranch) {
        return market.getBranch();
    }

    function getReputationToken() constant public returns (IReputationToken) {
        return market.getReportingWindow().getReputationToken();
    }

    function getBondHolder() constant public returns (address) {
        return bondHolder;
    }

    function getDisputedPayoutDistributionHash() constant public returns (bytes32) {
        return disputedPayoutDistributionHash;
    }

    function getBondRemainingToBePaidOut() constant public returns (uint256) {
        return bondRemainingToBePaidOut;
    }

    function balanceOf(address _address) constant public returns (uint256) {
        if (_address == bondHolder) {
            return 1;
        } else {
            return 0;
        }
    }

    function transfer(address _destinationAddress, uint256 _attotokens) public returns (bool) {
        require(_attotokens == 1);
        require(msg.sender == bondHolder);
        bondHolder = _destinationAddress;
        return true;
    }

    function totalSupply() public constant returns (uint256) {
        return 1;
    }
}
