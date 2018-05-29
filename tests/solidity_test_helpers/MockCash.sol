pragma solidity 0.4.20;


import 'trading/ICash.sol';
import 'Controlled.sol';
import 'libraries/ITyped.sol';
import 'TEST/MockVariableSupplyToken.sol';


contract MockCash is ITyped, MockVariableSupplyToken, ICash {
    address private depositEtherForAddressValue;
    uint256 private withdrawEtherAmountValue;
    address private withdrawEtherToAddressValue;
    uint256 private withdrawEthertoAmountValue;

    function reset() public {
        depositEtherForAddressValue = address(0);
        withdrawEtherAmountValue = 0;
        withdrawEtherToAddressValue = address(0);
        withdrawEthertoAmountValue = 0;
    }

    function getDepositEtherForAddressValue() public returns(address) {
        return depositEtherForAddressValue;
    }

    function getWithdrawEtherAmountValue() public returns(uint256) {
        return withdrawEtherAmountValue;
    }

    function getwithdrawEtherToAddressValue() public returns(address) {
        return withdrawEtherToAddressValue;
    }

    function getwithdrawEthertoAmountValue() public returns(uint256) {
        return withdrawEthertoAmountValue;
    }

    function resetWithdrawEtherToValues() public {
        withdrawEtherToAddressValue = address(0);
        withdrawEthertoAmountValue = 0;
    }

    function getTypeName() public view returns (bytes32) {
        return "Cash";
    }

    function depositEther() external payable returns(bool) {
        return true;
    }

    function depositEtherFor(address _to) external payable returns(bool) {
        depositEtherForAddressValue = _to;
        return true;
    }

    function withdrawEther(uint256 _amount) external returns(bool) {
        withdrawEtherAmountValue = _amount;
        return true;
    }

    function withdrawEtherTo(address _to, uint256 _amount) external returns(bool) {
        withdrawEtherToAddressValue = _to;
        withdrawEthertoAmountValue = _amount;
    }

    function withdrawEtherToIfPossible(address _to, uint256 _amount) external returns (bool) {
        return true;
    }
}
