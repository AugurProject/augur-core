pragma solidity 0.4.20;


import 'libraries/Delegator.sol';
import 'reporting/IFeeWindow.sol';
import 'IController.sol';


contract MockFeeTokenFactory {
    IFeeWindow private createFeeTokenFeeWindowValue;
    IFeeToken private setCreateFeeTokenValue;

    function getCreateFeeToken() public returns(IFeeToken) {
        return setCreateFeeTokenValue;
    }

    function setCreateFeeToken(IFeeToken _feeToken) public {
        setCreateFeeTokenValue = _feeToken;
    }

    function getCreateFeeTokenFeeWindowValue() public returns(IFeeWindow) {
        return createFeeTokenFeeWindowValue;
    }

    function createFeeToken(IController _controller, IFeeWindow _feeWindow) public returns (IFeeToken) {
        createFeeTokenFeeWindowValue = _feeWindow;
        return setCreateFeeTokenValue;
    }
}
