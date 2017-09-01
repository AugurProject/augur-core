pragma solidity ^0.4.13;

import 'ROOT/libraries/DelegationTarget.sol';
import 'ROOT/libraries/Initializable.sol';
import 'ROOT/libraries/Typed.sol';
import 'ROOT/libraries/token/VariableSupplyToken.sol';
import 'ROOT/reporting/Market.sol';


contract ShareToken is DelegationTarget, VariableSupplyToken, Typed, Initializable {

    //FIXME: Delegated contracts cannot currently use string values, so we will need to find a workaround if this hasn't been fixed before we release
    string constant public name = "Shares";
    uint256 constant public decimals = 18;
    string constant public symbol = "SHARE";

    Market private market;
    uint8 private outcome;

    function initialize(Market _market, uint8 _outcome) external beforeInitialized returns(bool) {
        endInitialization();
        market = _market;
        outcome = _outcome;
    }

    function createShares(address _owner, uint256 _fxpValue) onlyWhitelistedCallers external returns(bool) {
        mint(_owner, _fxpValue);
        return true;
    }

    function destroyShares(address _owner, uint256 _fxpValue) onlyWhitelistedCallers external returns(bool) {
        burn(_owner, _fxpValue);
        return true;
    }

    function getTypeName() constant returns(bytes32) {
        return "ShareToken";
    }

    function getMarket() constant public returns(Market) {
        return market;
    }

    function getOutcome() constant public returns(uint8) {
        return outcome;
    }

    function isShareToken() constant public returns(bool) {
        return true;
    }
}
