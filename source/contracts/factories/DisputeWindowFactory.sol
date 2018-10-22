pragma solidity 0.4.24;

import 'libraries/Delegator.sol';
import 'IController.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IDisputeWindow.sol';


contract DisputeWindowFactory {
    function createDisputeWindow(IController _controller, IUniverse _universe, uint256 _disputeWindowId) public returns (IDisputeWindow) {
        Delegator _delegator = new Delegator(_controller, "DisputeWindow");
        IDisputeWindow _disputeWindow = IDisputeWindow(_delegator);
        _disputeWindow.initialize(_universe, _disputeWindowId);
        return _disputeWindow;
    }
}
