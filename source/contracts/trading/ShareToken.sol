pragma solidity ^0.4.13;

import 'trading/IShareToken.sol';
import 'libraries/DelegationTarget.sol';
import 'libraries/token/VariableSupplyToken.sol';
import 'libraries/Typed.sol';
import 'libraries/Initializable.sol';
import 'reporting/IMarket.sol';


contract ShareToken is DelegationTarget, Typed, Initializable, VariableSupplyToken, IShareToken {

    //FIXME: Delegated contracts cannot currently use string values, so we will need to find a workaround if this hasn't been fixed before we release
    string constant public name = "Shares";
    uint256 constant public decimals = 0;
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
}
