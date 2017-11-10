pragma solidity 0.4.17;


import 'libraries/ITyped.sol';
import 'reporting/IMarket.sol';
import 'libraries/Ownable.sol';
import 'reporting/IReputationToken.sol';
import 'reporting/IUniverse.sol';


contract MockDisputeBond is ITyped, IDisputeBond, Ownable {
    IMarket private initializeMarketValue;
    address private initializeBondHolderValue;
    uint256 private initializeBondAmountValue;
    bytes32 private initializePayoutDistributionHashValue;
    IMarket private setMarketValue;
    bytes32 private setDisputedPayoutDistributionHashValue;
    uint256 private setBondRemainingToBePaidOutValue;

    /*
    * setters to feed the getters and impl of IReportingWindow
    */
    function getInitializeMarketValue() public returns(IMarket) {
        return initializeMarketValue;
    }

    function getInitializeBondHolderValue() public returns(address) {
        return initializeBondHolderValue;
    }

    function getInitializeBondAmountValue() public returns(uint256) {
        return initializeBondAmountValue;
    }

    function getInitializePayoutDistributionHashValue() public returns(bytes32) {
        return initializePayoutDistributionHashValue;
    }

    function setMarket(IMarket _market) public {
        setMarketValue = _market;
    }

    function setDisputedPayoutDistributionHash(bytes32 _setDisputedPayoutDistributionHashValue) public {
        setDisputedPayoutDistributionHashValue = _setDisputedPayoutDistributionHashValue;
    }

    function setBondRemainingToBePaidOut(uint256 _setBondRemainingToBePaidOutValue) public {
        setBondRemainingToBePaidOutValue = _setBondRemainingToBePaidOutValue;
    }

    function callCollectReportingFees(address _reporterAddress, uint256 _attoStake, bool _forgoFees, IReportingWindow _reportingWindow) public returns(uint256) {
        return _reportingWindow.collectDisputeBondReportingFees(_reporterAddress, _attoStake, _forgoFees);
    }

    function callDecreaseRepAvailableForExtraBondPayouts(IUniverse _universe, uint256 _amount) public returns(bool) {
        return _universe.decreaseRepAvailableForExtraBondPayouts(_amount);
    }

    function callDecreaseExtraDisputeBondRemainingToBePaidOut(IMarket _market, uint256 _amount) public returns(bool) {
        return _market.decreaseExtraDisputeBondRemainingToBePaidOut(_amount);
    }

    function callMigrateOutDisputeBond(IReputationToken _reputationToken, IReputationToken  _destination, address _reporter, uint256 _attotokens) public returns(bool) {
        return _reputationToken.migrateOutDisputeBond(_destination, _reporter, _attotokens);
    }

    function callMintForDisputeBondMigration(IReputationToken _reputationToken, uint256 _attotokens) public returns(bool) {
        return _reputationToken.mintForDisputeBondMigration(_attotokens);
    }

    /*
    * Impl of IReportingWindow and ITyped
     */
    function getTypeName() constant public returns (bytes32) {
        return "DisputeBond";
    }

    function initialize(IMarket _market, address _bondHolder, uint256 _bondAmount, bytes32 _payoutDistributionHash) public returns (bool) {
        initializeMarketValue = _market;
        initializeBondHolderValue = _bondHolder;
        initializeBondAmountValue = _bondAmount;
        initializePayoutDistributionHashValue = _payoutDistributionHash;
        return true;
    }

    function getMarket() constant public returns (IMarket) {
        return setMarketValue;
    }

    function getDisputedPayoutDistributionHash() constant public returns (bytes32) {
        return setDisputedPayoutDistributionHashValue;
    }

    function getBondRemainingToBePaidOut() constant public returns (uint256) {
        return setBondRemainingToBePaidOutValue;
    }
}
