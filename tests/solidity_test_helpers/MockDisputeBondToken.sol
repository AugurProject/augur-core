pragma solidity 0.4.17;


import 'libraries/ITyped.sol';
import 'reporting/IMarket.sol';


contract MockDisputeBondToken is ITyped, IDisputeBond {
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

    function callCollectReportingFees(address _reporterAddress, uint256 _attoStake, bool _forgoFees, IReportingWindow _reportingWindow) public returns(bool) {
        return _reportingWindow.collectDisputeBondReportingFees(_reporterAddress, _attoStake, _forgoFees);
    }

    function callDecreaseRepAvailableForExtraBondPayouts(IUniverse _universe, uint256 _amount) public returns(bool) {
        return _universe.decreaseRepAvailableForExtraBondPayouts(_amount);
    }

    function callDecreaseExtraDisputeBondRemainingToBePaidOut(IUniverse _universe, uint256 _amount) public returns(bool) {
        return _universe.decreaseExtraDisputeBondRemainingToBePaidOut(_amount);
    }

    /*
    * Impl of IReportingWindow and ITyped
     */
     function getTypeName() constant public returns (bytes32) {
        return "DisputeBondToken";
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
