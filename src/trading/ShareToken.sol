pragma solidity ^0.4.13;

import 'ROOT/trading/IShareToken.sol';
import 'ROOT/libraries/DelegationTarget.sol';
import 'ROOT/libraries/token/VariableSupplyToken.sol';
import 'ROOT/libraries/Typed.sol';
import 'ROOT/libraries/Initializable.sol';
import 'ROOT/reporting/IMarket.sol';


contract ShareToken is DelegationTarget, Typed, Initializable, VariableSupplyToken, IShareToken {

    //FIXME: Delegated contracts cannot currently use string values, so we will need to find a workaround if this hasn't been fixed before we release
    string constant public name = "Shares";
    uint256 constant public decimals = 18;
    string constant public symbol = "SHARE";

    IMarket private market;
    uint8 private outcome;

    function initialize(IMarket _market, uint8 _outcome) external beforeInitialized returns(bool) {
        endInitialization();
        market = _market;
        outcome = _outcome;
    }

    function createShares(address _owner, uint256 _fxpValue) external onlyWhitelistedCallers returns(bool) {
        mint(_owner, _fxpValue);
        return true;
    }

    function destroyShares(address _owner, uint256 _fxpValue) external onlyWhitelistedCallers returns(bool) {
        burn(_owner, _fxpValue);
        return true;
    }

    function getTypeName() constant returns(bytes32) {
        return "ShareToken";
    }

    function getMarket() external constant returns(IMarket) {
        return market;
    }

    function getOutcome() external constant returns(uint8) {
        return outcome;
    }

    function isShareToken() constant public returns(bool) {
        return true;
    }

    function transfer(address _to, uint256 _value) public returns(bool) {
        balances[msg.sender] = balances[msg.sender].sub(_value);
        balances[_to] = balances[_to].add(_value);
        Transfer(msg.sender, _to, _value);
        return true;
    }
}
