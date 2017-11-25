pragma solidity 0.4.18;


import 'libraries/token/BasicToken.sol';
import 'libraries/token/ERC20.sol';


contract MockStandardToken is ERC20, BasicToken {
    using SafeMathUint256 for uint256;
    address transferFromFromValue;
    address transferFromToValue;
    uint256 transferFromValueValue;
    address approveSpenderValue;
    uint256 approveValueValue;
    address allowanceOwnerValue;
    address allowanceSpenderValue;
    uint256 allowanceValue;

    function getTransferFromFromValue() public returns(address) {
        return transferFromFromValue;
    }

    function getTransferFromToValue() public returns(address) {
        return transferFromToValue;
    }

    function getTransferFromValueValue() public returns(uint256) {
        return transferFromValueValue;
    }

    function getApproveSpenderValue() public returns(address) {
        return approveSpenderValue;
    }
    
    function getApproveValueValue() public returns(uint256) {
        return approveValueValue;
    }

    function getAllowanceOwnerValue() public returns(address) {
        return allowanceOwnerValue;
    }
    
    function getAllowanceSpenderValue() public returns(address) {
        return allowanceSpenderValue;
    }

    function setAllowanceValue(uint256 _amount) public {
        allowanceValue = _amount;
    }

    function transferFrom(address _from, address _to, uint256 _value) public returns (bool) {
        transferFromFromValue = _from;
        transferFromToValue = _to;
        transferFromValueValue = _value;
        return true;
    }

    function approve(address _spender, uint256 _value) public returns (bool) {
        approveSpenderValue = _spender;
        approveValueValue = _value;
        return true;
    }

    function allowance(address _owner, address _spender) public view returns (uint256 remaining) {
        allowanceOwnerValue = _owner;
        allowanceSpenderValue = _spender;
        return allowanceValue;
    }

    function onTokenTransfer(address _from, address _to, uint256 _value) internal returns (bool) {
        return true;
    }
}
