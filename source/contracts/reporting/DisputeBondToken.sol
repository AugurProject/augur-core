pragma solidity 0.4.17;


import 'reporting/IDisputeBond.sol';
import 'libraries/DelegationTarget.sol';
import 'libraries/ITyped.sol';
import 'libraries/Initializable.sol';
import 'libraries/token/ERC20Basic.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReputationToken.sol';
import 'reporting/IMarket.sol';
import 'libraries/math/SafeMathUint256.sol';


// CONSIDER: This could probably just be made Ownable instead if implementing ERC20Basic
contract DisputeBondToken is DelegationTarget, ITyped, Initializable, ERC20Basic, IDisputeBond {
    using SafeMathUint256 for uint256;

    IMarket private market;
    address private bondHolder;
    bytes32 private disputedPayoutDistributionHash;
    uint256 private bondRemainingToBePaidOut;
    uint256 private bondAmount;

    function initialize(IMarket _market, address _bondHolder, uint256 _bondAmount, bytes32 _payoutDistributionHash) public beforeInitialized returns (bool) {
        endInitialization();
        market = _market;
        bondHolder = _bondHolder;
        disputedPayoutDistributionHash = _payoutDistributionHash;
        bondAmount = _bondAmount;
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
        if (bondRemainingToBePaidOut < bondAmount) {
            uint256 _amountToDeductFromExtraPayout = _amountToTransfer.min(bondAmount - bondRemainingToBePaidOut);
            getUniverse().decreaseExtraDisputeBondRemainingToBePaidOut(_amountToDeductFromExtraPayout); 
        }
        _reputationToken.transfer(bondHolder, _amountToTransfer);
        return true;
    }

    // NOTE: The UI should warn users about doing this before REP has migrated fully out of the forking universe in order to get their extra payout, which is sourced from REP migrated to other Universes. There is no penalty for waiting (In fact waiting will only ever get them a greater payout)
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
        // We recalculate the amount since migrating may have earned us a bonus
        _amountToTransfer = _destinationReputationToken.balanceOf(this);
        bondRemainingToBePaidOut = bondRemainingToBePaidOut.sub(_amountToTransfer);
        uint256 _amountMinted = mintRepTokensForBondMigration(_destinationReputationToken);
        bondRemainingToBePaidOut = bondRemainingToBePaidOut.sub(_amountMinted);
        _amountToTransfer = _amountToTransfer.add(_amountMinted);
        if (bondRemainingToBePaidOut < bondAmount) {
            uint256 _amountToDeductFromExtraPayout = _amountToTransfer.min(bondAmount - bondRemainingToBePaidOut);
            getUniverse().decreaseExtraDisputeBondRemainingToBePaidOut(_amountToDeductFromExtraPayout); 
        }
        _destinationReputationToken.transfer(bondHolder, _amountToTransfer);
        return true;
    }

    function mintRepTokensForBondMigration(IReputationToken _destinationReputationToken) private returns (uint256) {
        IUniverse _universe = market.getUniverse();
        IUniverse _disputeUniverse = _universe.getOrCreateChildUniverse(disputedPayoutDistributionHash);

        uint256 _amountToMint = bondRemainingToBePaidOut;
        uint256 _amountNeededByUniverse = _universe.getExtraDisputeBondRemainingToBePaidOut();
        uint256 _amountAvailableToMatch = _disputeUniverse.getRepAvailableForExtraBondPayouts();

        uint256 _maximumAmountMintable = _amountAvailableToMatch.mul(_amountToMint).div(_amountNeededByUniverse);
        _amountToMint = _amountToMint.min(_maximumAmountMintable);

        _disputeUniverse.decreaseRepAvailableForExtraBondPayouts(_amountToMint);
        _destinationReputationToken.mintForDisputeBondMigration(_amountToMint);
        return _amountToMint;
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
