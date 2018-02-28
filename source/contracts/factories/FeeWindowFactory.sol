pragma solidity 0.4.20;

import 'libraries/Delegator.sol';
import 'IController.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IFeeWindow.sol';


contract FeeWindowFactory {
    function createFeeWindow(IController _controller, IUniverse _universe, uint256 _feeWindowId) public returns (IFeeWindow) {
        Delegator _delegator = new Delegator(_controller, "FeeWindow");
        IFeeWindow _feeWindow = IFeeWindow(_delegator);
        _feeWindow.initialize(_universe, _feeWindowId);
        return _feeWindow;
    }
}
