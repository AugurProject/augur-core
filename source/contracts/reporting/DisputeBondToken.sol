pragma solidity ^0.4.17;

import 'reporting/IDisputeBond.sol';
import 'libraries/DelegationTarget.sol';
import 'libraries/Typed.sol';
import 'libraries/Initializable.sol';
import 'libraries/token/ERC20Basic.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReputationToken.sol';
import 'reporting/IMarket.sol';
import 'libraries/math/SafeMathUint256.sol';


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
        require(getUniverse().getForkingMarket() != market);
        IReputationToken _reputationToken = getReputationToken();
        uint256 _amountToTransfer = _reputationToken.balanceOf(this);
        bondRemainingToBePaidOut = bondRemainingToBePaidOut.sub(_amountToTransfer);
        _reputationToken.transfer(bondHolder, _amountToTransfer);
        return true;
    }

    // FIXME: We should be minting coins in this scenario in order to achieve 2x target payout for bond holders during a fork.  Ideally, the amount minted is capped at the amount of tokens redeemed on other universes, so we may have to require the user to supply universes to deduct from with their call to this.
    function withdrawToUniverse(IUniverse _shadyUniverse) public returns (bool) {
        require(msg.sender == bondHolder);
        require(!market.isContainerForDisputeBondToken(this) || getUniverse().getForkingMarket() == market);
        bool _isChildOfMarketUniverse = market.getReportingWindow().getUniverse().isParentOf(_shadyUniverse);
        require(_isChildOfMarketUniverse);
        IUniverse _legitUniverse = _shadyUniverse;
        require(_legitUniverse.getParentPayoutDistributionHash() != disputedPayoutDistributionHash);
        IReputationToken _reputationToken = getReputationToken();
        uint256 _amountToTransfer = _reputationToken.balanceOf(this);
        IReputationToken _destinationReputationToken = _legitUniverse.getReputationToken();
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

    function getUniverse() constant public returns (IUniverse) {
        return market.getUniverse();
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
