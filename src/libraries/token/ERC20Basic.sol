pragma solidity ^0.4.13;


/**
 * @title ERC20Basic
 * @dev Simpler version of ERC20 interface
 * @dev see https://github.com/ethereum/EIPs/issues/179
 */
contract ERC20Basic {
    uint256 internal totalSupply;

    event Transfer(address indexed from, address indexed to, uint256 value);

    function getTotalSupply() public constant returns (uint256) {
        return totalSupply;
    }

    function balanceOf(address _who) public constant returns (uint256);
    function transfer(address _to, uint256 _value) public returns (bool);
}
