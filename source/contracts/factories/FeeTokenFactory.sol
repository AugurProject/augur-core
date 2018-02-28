pragma solidity 0.4.20;

import 'reporting/IFeeToken.sol';
import 'IController.sol';
import 'libraries/Delegator.sol';
import 'reporting/IFeeWindow.sol';


contract FeeTokenFactory {
    function createFeeToken(IController _controller, IFeeWindow _feeWindow) public returns (IFeeToken) {
        Delegator _delegator = new Delegator(_controller, "FeeToken");
        IFeeToken _feeToken = IFeeToken(_delegator);
        _feeToken.initialize(_feeWindow);
        return _feeToken;
    }
}