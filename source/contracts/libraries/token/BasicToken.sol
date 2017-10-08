pragma solidity 0.4.17;


import 'libraries/token/ERC20Basic.sol';
import 'libraries/math/SafeMathUint256.sol';


/**
 * @title Basic token
 * @dev Basic version of StandardToken, with no allowances.
 */
contract BasicToken is ERC20Basic {
    using SafeMathUint256 for uint256;

    uint256 internal supply;
    mapping(address => uint256) internal balances;

    /**
    * @dev transfer token for a specified address
    * @param _to The address to transfer to.
    * @param _value The amount to be transferred.
    */
    function transfer(address _to, uint256 _value) public returns(bool) {
        balances[msg.sender] = balances[msg.sender].sub(_value);
        balances[_to] = balances[_to].add(_value);
        Transfer(msg.sender, _to, _value);
        return true;
    }

    /**
    * @dev Gets the balance of the specified address.
    * @param _owner The address to query the the balance of.
    * @return An uint256 representing the amount owned by the passed address.
    */
    function balanceOf(address _owner) public constant returns (uint256 balance) {
        return balances[_owner];
    }

    function getBalance(address _address) public constant returns (uint256) {
        return balances[_address];
    }

    function totalSupply() public constant returns (uint256) {
        return supply;
    }
}
