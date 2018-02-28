pragma solidity ^0.4.20;

import 'TEST/MockStandardToken.sol';


contract MockVariableSupplyToken is MockStandardToken {
    uint256 private setBalanceOfValue;
    address private transferToValue;
    uint256 private transferValueValue;
    uint256 private setTotalSupplyValue;
    uint256[] private transferAmounts;
    address[] private transferAddresses;
    uint256[] private balanceOfAmounts;
    address[] private balanceOfAddresses;
    address private transferFromFromValue;
    address private transferFromToValue;
    uint256 private transferFromValueValue;
    event Mint(address indexed target, uint256 value);
    event Burn(address indexed target, uint256 value);

    function setBalanceOf(uint256 _balance) public {
        setBalanceOfValue = _balance;
    }

    function getTransferToValue() public returns(address) {
        return transferToValue;
    }

    function getTransferValueValue() public returns(uint256) {
        return transferValueValue;
    }

    function resetBalanceOfValues() public {
        setBalanceOfValue = 0;
        balanceOfAmounts = [0];
        balanceOfAddresses = [0];
    }

    function resetTransferToValues() public {
        transferToValue = address(0);
        transferValueValue = 0;
        transferAmounts = [0];
        transferAddresses = [0];
    }

    function getTransferValueFor(address _to) public returns(uint256) {
        for (uint256 j = 0; j < transferAddresses.length; j++) {
            if (transferAddresses[j] == _to) {
                return transferAmounts[j];
            }
        }
        return 0;
    }

    function setBalanceOfValueFor(address _to, uint256 _value) public returns(uint256) {
        balanceOfAmounts.push(_value);
        balanceOfAddresses.push(_to);
    }

    function setTotalSupply(uint256 _totalSupply) public {
        setTotalSupplyValue = _totalSupply;
    }

    function getTransferFromFromValue() public returns(address) {
        return transferFromFromValue;
    }

    function getTransferFromToValue() public returns (address) {
        return transferFromToValue;
    }

    function getTransferFromValueValue() public returns (uint256) {
        return transferFromValueValue;
    }

    function mint(address _target, uint256 _amount) internal returns (bool) {
        return true;
    }

    function burn(address _target, uint256 _amount) internal returns (bool) {
        return true;
    }

    function balanceOf(address _owner) public view returns (uint256) {
        for (uint256 j = 0; j < balanceOfAddresses.length; j++) {
            if (balanceOfAddresses[j] == _owner) {
                return balanceOfAmounts[j];
            }
        }
        return setBalanceOfValue;
    }

    function transfer(address _to, uint256 _value) public returns (bool) {
        transferToValue = _to;
        transferValueValue = _value;
        transferAmounts.push(_value);
        transferAddresses.push(_to);
        return true;
    }

    function totalSupply() public view returns (uint256) {
        return setTotalSupplyValue;
    }

    function transferFrom(address _from, address _to, uint256 _value) public returns (bool) {
        transferFromFromValue = _from;
        transferFromToValue = _to;
        transferFromValueValue = _value;
        return true;
    }
}
