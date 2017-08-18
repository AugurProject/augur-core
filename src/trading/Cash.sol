pragma solidity ^0.4.13;

import 'ROOT/libraries/Typed.sol';
import 'ROOT/libraries/token/VariableSupplyToken.sol';
import 'ROOT/Controller.sol';


/**
 * @title Cash
 * @dev ETH wrapper contract to make it look like an ERC20 token.
 */
contract Cash is Controlled, Typed, VariableSupplyToken {
    using SafeMathUint256 for uint256;

    event InitiateWithdrawEther(address indexed sender, uint256 value, uint256 balance);
    enum WithdrawState { Failed, Withdrawn, Initiated }

    string constant public name = "Cash";
    string constant public symbol = "CASH";
    uint256 constant public decimals = 18;
    mapping(address => uint256) public initiated;

    function depositEther() external payable onlyInGoodTimes returns(bool) {
        mint(msg.sender, msg.value);
        return true;
    }

    function withdrawEther(uint256 _amount) external onlyInGoodTimes returns(WithdrawState) {
        require(1 <= _amount && _amount <= balances[msg.sender]);
        var _initiatedTimestamp = initiated[msg.sender];

        // if the withdraw clock hasn't been started, then start it and return early
        if (_initiatedTimestamp == 0) {
            initiated[msg.sender] = block.timestamp;
            InitiateWithdrawEther(msg.sender, _amount, balances[msg.sender]);
            return WithdrawState.Initiated;
        }

        // FIXME: attacker can initiate a withdraw of 1 unit, wait 3 days, then launch an attack and then immediately withdraw everything
        require(_initiatedTimestamp + 3 days <= block.timestamp);
        burn(msg.sender, _amount);
        initiated[msg.sender] = 0;
        msg.sender.transfer(_amount);
        return WithdrawState.Withdrawn;
    }

    // FIXME: this is necessary until we figure out a better way to check to see if a market's denomination token is a shareToken or not.  right now this is the only other valid denomination token so this hack works, but it won't when we support arbitrary denomination tokens.
    function getMarket() constant returns (bool) {
        return false;
    }

    function getTypeName() constant returns (bytes32) {
        return "Cash";
    }
}
