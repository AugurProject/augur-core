pragma solidity 0.4.20;


import 'libraries/token/BasicToken.sol';
import 'libraries/token/ERC20.sol';


/**
 * @title Standard ERC20 token
 *
 * @dev Implementation of the basic standard token.
 * @dev https://github.com/ethereum/EIPs/issues/20
 * @dev Based on code by FirstBlood: https://github.com/Firstbloodio/token/blob/master/smart_contract/FirstBloodToken.sol
 */
contract StandardToken is ERC20, BasicToken {
    using SafeMathUint256 for uint256;

    // Approvals of this amount are simply considered an everlasting approval which is not decremented when transfers occur
    uint256 public constant ETERNAL_APPROVAL_VALUE = 2 ** 256 - 1;

    mapping (address => mapping (address => uint256)) internal allowed;

    /**
    * @dev Transfer tokens from one address to another
    * @param _from address The address which you want to send tokens from
    * @param _to address The address which you want to transfer to
    * @param _value uint256 the amout of tokens to be transfered
    */
    function transferFrom(address _from, address _to, uint256 _value) public returns (bool) {
        uint256 _allowance = allowed[_from][msg.sender];

        if (_allowance != ETERNAL_APPROVAL_VALUE) {
            allowed[_from][msg.sender] = _allowance.sub(_value);
        }
        internalTransfer(_from, _to, _value);
        return true;
    }

    /**
    * @dev Aprove the passed address to spend the specified amount of tokens on behalf of msg.sender.
    * @param _spender The address which will spend the funds.
    * @param _value The amount of tokens to be spent.
    */
    function approve(address _spender, uint256 _value) public returns (bool) {
        approveInternal(msg.sender, _spender, _value);
        return true;
    }

    /**
    * @dev Function to check the amount of tokens that an owner allowed to a spender.
    * @param _owner address The address which owns the funds.
    * @param _spender address The address which will spend the funds.
    * @return A uint256 specifing the amount of tokens still avaible for the spender.
    */
    function allowance(address _owner, address _spender) public view returns (uint256 remaining) {
        return allowed[_owner][_spender];
    }

   /**
   * @dev Increase the amount of tokens that an owner allowed to a spender.
   *
   * Approve should be called when allowed[_spender] == 0. To increment allowed value is better to use this function to avoid 2 calls (and wait until the first transaction is mined)
   * @param _spender The address which will spend the funds.
   * @param _addedValue The amount of tokens to increase the allowance by.
   */
    function increaseApproval(address _spender, uint _addedValue) public returns (bool) {
        approveInternal(msg.sender, _spender, allowed[msg.sender][_spender].add(_addedValue));
        return true;
    }

  /**
   * @dev Decrease the amount of tokens that an owner allowed to a spender.
   *
   * approve should be called when allowed[_spender] == 0. To decrement allowed value is better to use this function to avoid 2 calls (and wait until the first transaction is mined)
   * @param _spender The address which will spend the funds.
   * @param _subtractedValue The amount of tokens to decrease the allowance by.
   */
    function decreaseApproval(address _spender, uint _subtractedValue) public returns (bool) {
        uint oldValue = allowed[msg.sender][_spender];
        if (_subtractedValue > oldValue) {
            approveInternal(msg.sender, _spender, 0);
        } else {
            approveInternal(msg.sender, _spender, oldValue.sub(_subtractedValue));
        }
        return true;
    }

    function approveInternal(address _owner, address _spender, uint256 _value) internal returns (bool) {
        allowed[_owner][_spender] = _value;
        Approval(_owner, _spender, _value);
        return true;
    }
}
