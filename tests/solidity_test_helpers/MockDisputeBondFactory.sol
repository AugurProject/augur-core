pragma solidity 0.4.17;


import 'libraries/Delegator.sol';
import 'reporting/IDisputeBond.sol';
import 'reporting/IMarket.sol';
import 'IController.sol';


contract MockDisputeBondFactory {
    IMarket private createDisputeBondMarketValue;
    address private createDisputeBondBondHolderValue;
    uint256 private createDisputeBondAmountValue;
    bytes32 private createDisputeBondPayoutDistributionHash;
    IDisputeBond private setCreateDisputeBondValue;

    function getCreateDisputeBondMarket() public returns(IMarket) {
        return createDisputeBondMarketValue;
    }

    function getCreateDisputeBondBondHolder() public returns(address) {
        return createDisputeBondBondHolderValue;
    }

    function getCreateDisputeBondAmountValue() public returns(uint256) {
        return createDisputeBondAmountValue;
    }

    function getCreateDisputeBondPayoutDistributionHash() public returns(bytes32) {
        return createDisputeBondPayoutDistributionHash;
    }

    function setCreateDisputeBond(IDisputeBond _bond) public {
        setCreateDisputeBondValue = _bond;
    }

    function createDisputeBond(IController _controller, IMarket _market, address _bondHolder, uint256 _bondAmount, bytes32 _payoutDistributionHash) public returns (IDisputeBond) {
        createDisputeBondMarketValue = _market;
        createDisputeBondBondHolderValue = _bondHolder;
        createDisputeBondAmountValue = _bondAmount;
        createDisputeBondPayoutDistributionHash = _payoutDistributionHash;
        return setCreateDisputeBondValue;
    }
}
