pragma solidity 0.4.20;

import 'reporting/IFeeToken.sol';
import 'reporting/IFeeWindow.sol';
import 'libraries/DelegationTarget.sol';
import 'libraries/token/VariableSupplyToken.sol';


contract FeeToken is DelegationTarget, VariableSupplyToken, IFeeToken {

    string constant public name = "FeeToken";
    string constant public symbol = "FEE";
    uint8 constant public decimals = 0;

    IFeeWindow private feeWindow;

    function initialize(IFeeWindow _feeWindow) public beforeInitialized returns (bool) {
        endInitialization();
        feeWindow = _feeWindow;
        return true;
    }

    function getFeeWindow() public afterInitialized view returns (IFeeWindow) {
        return feeWindow;
    }

    function feeWindowBurn(address _target, uint256 _amount) public afterInitialized returns (bool) {
        require(IFeeWindow(msg.sender) == feeWindow);
        burn(_target, _amount);
        return true;
    }

    function mintForReportingParticipant(address _target, uint256 _amount) public afterInitialized returns (bool) {
        require(IFeeWindow(msg.sender) == feeWindow);
        mint(_target, _amount);
        return true;
    }

    function onTokenTransfer(address _from, address _to, uint256 _value) internal returns (bool) {
        controller.getAugur().logFeeTokenTransferred(feeWindow.getUniverse(), _from, _to, _value);
        return true;
    }

    function onMint(address _target, uint256 _amount) internal returns (bool) {
        controller.getAugur().logFeeTokenMinted(feeWindow.getUniverse(), _target, _amount);
        return true;
    }

    function onBurn(address _target, uint256 _amount) internal returns (bool) {
        controller.getAugur().logFeeTokenBurned(feeWindow.getUniverse(), _target, _amount);
        return true;
    }
}
