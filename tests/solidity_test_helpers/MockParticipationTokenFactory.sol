pragma solidity 0.4.18;

import 'libraries/Delegator.sol';
import 'reporting/IFeeWindow.sol';
import 'reporting/IFeeWindow.sol';
import 'IController.sol';


contract MockFeeWindowFactory {

    IFeeWindow private feeWindowValue;
    IController private createFeeWindowControllerValue;
    IFeeWindow private createFeeWindowFeeWindow;

    function setFeeWindowValue(IFeeWindow _feeWindowValue) public {
        feeWindowValue = _feeWindowValue;
    }

    function getCreateFeeWindowControllerValue() public returns(IController) {
        return createFeeWindowControllerValue;
    }

    function getCreateFeeWindowFeeWindow() public returns(IFeeWindow) {
        return createFeeWindowFeeWindow;
    }

    function createFeeWindow(IController _controller, IFeeWindow _feeWindow) public returns (IFeeWindow) {
        createFeeWindowControllerValue = _controller;
        createFeeWindowFeeWindow = _feeWindow;
        return feeWindowValue;
    }
}
