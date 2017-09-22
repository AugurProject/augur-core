pragma solidity ^0.4.13;


contract Utils {
    function getETHBalance(address _address) public returns (uint256) {
        return _address.balance;
    }
}
