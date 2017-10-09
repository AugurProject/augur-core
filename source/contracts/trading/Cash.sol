pragma solidity 0.4.17;


import 'trading/ICash.sol';
import 'Controlled.sol';
import 'libraries/Typed.sol';
import 'libraries/token/VariableSupplyToken.sol';


/**
 * @title Cash
 * @dev ETH wrapper contract to make it look like an ERC20 token.
 */
contract Cash is Controlled, Typed, VariableSupplyToken, ICash {
    using SafeMathUint256 for uint256;

    string constant public name = "Cash";
    string constant public symbol = "CASH";
    uint256 constant public decimals = 18;

    function depositEther() external payable onlyInGoodTimes returns(bool) {
        mint(msg.sender, msg.value);
        return true;
    }

    function depositEtherFor(address _to) external payable onlyInGoodTimes returns(bool) {
        mint(_to, msg.value);
        return true;
    }

    function withdrawEther(uint256 _amount) external returns(bool) {
        require(_amount > 0 && _amount <= balances[msg.sender]);
        burn(msg.sender, _amount);
        msg.sender.call.value(_amount)();
        return true;
    }

    function withdrawEtherTo(address _to, uint256 _amount) external returns(bool) {
        require(_amount > 0 && _amount <= balances[msg.sender]);
        burn(msg.sender, _amount);
        _to.call.value(_amount)();
        return true;
    }

    function getTypeName() public view returns (bytes32) {
        return "Cash";
    }
}
