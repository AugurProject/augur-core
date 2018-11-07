pragma solidity 0.4.24;

import 'libraries/CloneFactory.sol';
import 'IController.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IDisputeWindow.sol';
import 'IControlled.sol';


contract DisputeWindowFactory is CloneFactory {
    function createDisputeWindow(IController _controller, IUniverse _universe, uint256 _disputeWindowId) public returns (IDisputeWindow) {
        IDisputeWindow _disputeWindow = IDisputeWindow(createClone(_controller.lookup("DisputeWindow")));
        IControlled(_disputeWindow).setController(_controller);
        _disputeWindow.initialize(_universe, _disputeWindowId);
        return _disputeWindow;
    }
}
