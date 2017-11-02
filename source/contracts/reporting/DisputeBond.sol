pragma solidity 0.4.18;


import '../reporting/IDisputeBond.sol';
import '../libraries/DelegationTarget.sol';
import '../libraries/ITyped.sol';
import '../libraries/Initializable.sol';
import '../libraries/Ownable.sol';
import '../reporting/IUniverse.sol';
import '../reporting/IReputationToken.sol';
import '../reporting/IMarket.sol';
import '../libraries/Extractable.sol';
import '../libraries/math/SafeMathUint256.sol';
import '../reporting/Reporting.sol';
import '../libraries/Extractable.sol';


contract DisputeBond is DelegationTarget, Extractable, ITyped, Initializable, Ownable, IDisputeBond {
    using SafeMathUint256 for uint256;

    IMarket private market;
    bytes32 private disputedPayoutDistributionHash;
    uint256 private bondRemainingToBePaidOut;
    uint256 private bondAmount;
    // We cache a reference to this since if a fork occurs and this is disavowed the REP token of the abandoning market will be incorrect
    IReputationToken private reputationToken;

    function initialize(IMarket _market, address _bondHolder, uint256 _bondAmount, bytes32 _payoutDistributionHash) public onlyInGoodTimes beforeInitialized returns (bool) {
        endInitialization();
        market = _market;
        owner = _bondHolder;
        disputedPayoutDistributionHash = _payoutDistributionHash;
        bondAmount = _bondAmount;
        bondRemainingToBePaidOut = _bondAmount * Reporting.getBondPayoutMultiplier();
        reputationToken = _market.getUniverse().getReputationToken();
        return true;
    }

    function withdraw(bool forgoFees) public onlyOwner onlyInGoodTimes returns (bool) {
        require(market.isContainerForDisputeBond(this));
        bool _isFinalized = market.getReportingState() == IMarket.ReportingState.FINALIZED;
        require(_isFinalized && market.getFinalPayoutDistributionHash() != disputedPayoutDistributionHash);
        require(getUniverse().getForkingMarket() != market);
        uint256 _amountToTransfer = reputationToken.balanceOf(this);
        if (bondRemainingToBePaidOut > bondAmount) {
            uint256 _amountToCollectFeesOn = _amountToTransfer.min(bondRemainingToBePaidOut - bondAmount);
            market.getReportingWindow().collectDisputeBondReportingFees(owner, _amountToCollectFeesOn, forgoFees);
        }
        bondRemainingToBePaidOut = bondRemainingToBePaidOut.sub(_amountToTransfer);
        reputationToken.transfer(owner, _amountToTransfer);
        return true;
    }

    function withdrawDisavowedTokens() public onlyOwner onlyInGoodTimes returns (bool) {
        require(!market.isContainerForDisputeBond(this));
        require(getUniverse().getForkingMarket() != market);
        uint256 _amountToTransfer = reputationToken.balanceOf(this);
        bondRemainingToBePaidOut = bondRemainingToBePaidOut.sub(_amountToTransfer);
        reputationToken.transfer(owner, _amountToTransfer);
        return true;
    }

    // This function is only available to bond holders for the forking market. Other bond holders in the forking universe must use the redeemDisavowedTokens method
    // NOTE: The UI should warn users about doing this before REP has migrated fully out of the forking universe in order to get their extra payout, which is sourced from REP migrated to other Universes. There is no penalty for waiting (In fact waiting will only ever get them a greater payout)
    function withdrawToUniverse(IUniverse _shadyUniverse) public onlyOwner onlyInGoodTimes returns (bool) {
        IUniverse _universe = getUniverse();
        require(_universe.getForkingMarket() == market);
        bool _isChildOfMarketUniverse = market.getReportingWindow().getUniverse().isParentOf(_shadyUniverse);
        require(_isChildOfMarketUniverse);

        IUniverse _legitUniverse = _shadyUniverse;
        require(_legitUniverse.getParentPayoutDistributionHash() != disputedPayoutDistributionHash);
        IReputationToken _reputationToken = reputationToken;

        // Migrate out the REP balance of this bond to REP in the destination Universe
        uint256 _amountToTransfer = _reputationToken.balanceOf(this);
        IReputationToken _destinationReputationToken = _legitUniverse.getReputationToken();
        _reputationToken.migrateOutDisputeBond(_destinationReputationToken, this, _amountToTransfer);

        // We recalculate the amount we now have since migrating may have earned us a bonus
        _amountToTransfer = _destinationReputationToken.balanceOf(this);
        bondRemainingToBePaidOut = bondRemainingToBePaidOut.sub(_amountToTransfer);

        // Mint tokens in the new Universe if appropriate
        uint256 _amountMinted = mintRepTokensForBondMigration(_destinationReputationToken);
        bondRemainingToBePaidOut = bondRemainingToBePaidOut.sub(_amountMinted);
        _amountToTransfer = _amountToTransfer.add(_amountMinted);

        // Adjust accounting for how much extra bond payout debt exists in this universe
        if (bondRemainingToBePaidOut < bondAmount) {
            uint256 _amountToDeductFromExtraPayout = _amountToTransfer.min(bondAmount - bondRemainingToBePaidOut);
            market.decreaseExtraDisputeBondRemainingToBePaidOut(_amountToDeductFromExtraPayout);
        }

        // Send the bond holder the destination Universe REP
        _destinationReputationToken.transfer(owner, _amountToTransfer);
        return true;
    }

    // When migrating a dispute bond to a new universe we attempt and mint REP to pay the full bond payout amount. We do this by matching REP migrated to an alternate universe
    function mintRepTokensForBondMigration(IReputationToken _destinationReputationToken) private onlyInGoodTimes returns (uint256) {
        IUniverse _disputeUniverse = market.getUniverse().getOrCreateChildUniverse(disputedPayoutDistributionHash);

        uint256 _amountToMint = bondRemainingToBePaidOut;
        uint256 _amountNeededByUniverse = market.getExtraDisputeBondRemainingToBePaidOut();
        uint256 _amountAvailableToMatch = _disputeUniverse.getRepAvailableForExtraBondPayouts();

        uint256 _maximumAmountMintable = _amountAvailableToMatch.mul(_amountToMint).div(_amountNeededByUniverse);
        _amountToMint = _amountToMint.min(_maximumAmountMintable);

        _disputeUniverse.decreaseRepAvailableForExtraBondPayouts(_amountToMint);
        _destinationReputationToken.mintForDisputeBondMigration(_amountToMint);
        return _amountToMint;
    }

    function withdrawInEmergency() public onlyOwner onlyInBadTimes returns (bool) {
        reputationToken.transfer(owner, reputationToken.balanceOf(this));
        return true;
    }

    function getTypeName() constant public returns (bytes32) {
        return "DisputeBond";
    }

    function getMarket() constant public returns (IMarket) {
        return market;
    }

    function getUniverse() constant public returns (IUniverse) {
        return market.getUniverse();
    }

    function getDisputedPayoutDistributionHash() constant public returns (bytes32) {
        return disputedPayoutDistributionHash;
    }

    function getBondRemainingToBePaidOut() constant public returns (uint256) {
        return bondRemainingToBePaidOut;
    }

    // Disallow REP extraction
    function getProtectedTokens() internal returns (address[] memory) {
        address[] memory _protectedTokens = new address[](1);
        _protectedTokens[0] = reputationToken;
        return _protectedTokens;
    }
}
