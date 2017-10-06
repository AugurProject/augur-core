pragma solidity ^0.4.17;


contract Utils {
    function getETHBalance(address _address) public returns (uint256) {
        return _address.balance;
    }
}
