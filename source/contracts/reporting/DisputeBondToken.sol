pragma solidity 0.4.17;


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
    uint256 private bonusAmountInPayout;

    function initialize(IMarket _market, address _bondHolder, uint256 _bondAmount, bytes32 _payoutDistributionHash) public beforeInitialized returns (bool) {
        endInitialization();
        market = _market;
        bondHolder = _bondHolder;
        disputedPayoutDistributionHash = _payoutDistributionHash;
        bonusAmountInPayout = _bondAmount * 1; // TODO put facotr in Reporting
        getUniverse().increaseExtraDisputeBondRemainingToBePaidOut(bonusAmountInPayout);
        bondRemainingToBePaidOut = _bondAmount + bonusAmountInPayout;
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
        // TODO adjust bonusAmountInPayout
        _reputationToken.transfer(bondHolder, _amountToTransfer);
        return true;
    }

    // NOTE: The UI should warn users about doing this before REP has migrated fully out of the forking universe in order to get their extra payout, which is sourced from REP migrated to other Universes. They can always call again however and there is no penalty for waiting.
    function withdrawToUniverse(IUniverse _shadyUniverse) public returns (bool) {
        require(msg.sender == bondHolder);
        IUniverse _universe = getUniverse();
        require(!market.isContainerForDisputeBondToken(this) || _universe.getForkingMarket() == market);
        bool _isChildOfMarketUniverse = market.getReportingWindow().getUniverse().isParentOf(_shadyUniverse);
        require(_isChildOfMarketUniverse);
        IUniverse _legitUniverse = _shadyUniverse;
        require(_legitUniverse.getParentPayoutDistributionHash() != disputedPayoutDistributionHash);
        IReputationToken _reputationToken = getReputationToken();
        uint256 _amountToTransfer = _reputationToken.balanceOf(this);
        IReputationToken _destinationReputationToken = _legitUniverse.getReputationToken();
        _reputationToken.migrateOut(_destinationReputationToken, this, _amountToTransfer);
        bondRemainingToBePaidOut = bondRemainingToBePaidOut.sub(_amountToTransfer);
        IUniverse _disputeUniverse = _universe.getOrCreateChildUniverse(disputedPayoutDistributionHash);
        // TODO handle bonusAmountInPayout
        uint256 _amountToMint = _disputeUniverse.deductDisputeBondExtraMintAmount(bondRemainingToBePaidOut, _universe.getExtraDisputeBondRemainingToBePaidOut()); // Deducts from disputeUniverse pool available and returns the amount to mint in this universe
        _universe.deductExtraDisputeBondRemainingToBePaidOut(_amountToMint);
        _destinationReputationToken.mintForDisputeBondMigration(_amountToMint);
        _amountToTransfer = _amountToTransfer.add(_amountToMint);
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

    function totalSupply() public view returns (uint256) {
        return 1;
    }
}
