pragma solidity 0.4.17;


import 'trading/IShareToken.sol';
import 'libraries/DelegationTarget.sol';
import 'libraries/token/VariableSupplyToken.sol';
import 'libraries/ITyped.sol';
import 'libraries/Initializable.sol';
import 'reporting/IMarket.sol';
import 'libraries/Extractable.sol';


contract ShareToken is DelegationTarget, Extractable, ITyped, Initializable, VariableSupplyToken, IShareToken {

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

    function getTypeName() public view returns(bytes32) {
        return "ShareToken";
    }

    function getMarket() external view returns(IMarket) {
        return market;
    }

    function getOutcome() external view returns(uint8) {
        return outcome;
    }

    function isShareToken() public pure returns(bool) {
        return true;
    }

    function emitTransferLogs(address _from, address _to, uint256 _value) internal returns (bool) {
        Transfer(_from, _to, _value);
        controller.getAugur().logShareTokensTransferred(market.getUniverse(), _from, _to, _value);
        return true;
    }

    function onMint(address _target, uint256 _amount) internal returns (bool) {
        controller.getAugur().logShareTokenMinted(market.getUniverse(), _target, _amount);
        return true;
    }

    function onBurn(address _target, uint256 _amount) internal returns (bool) {
        controller.getAugur().logShareTokenBurned(market.getUniverse(), _target, _amount);
        return true;
    }

    function getProtectedTokens() internal returns (address[] memory) {
        return new address[](0);
    }
}
