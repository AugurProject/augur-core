pragma solidity 0.4.24;


import 'IController.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IDisputeWindow.sol';


contract MockDisputeWindowFactory {
    IUniverse private createDisputeWindowUniverseValue;
    IDisputeWindow private createDisputeWindowValue;
    uint256 private createdisputeWindowIdValue;

    function getCreateDisputeWindowUniverseValue() public returns(IUniverse) {
        return createDisputeWindowUniverseValue;
    }

    function getCreateDisputeWindowValue(IDisputeWindow _disputeWindowValue) public returns(IDisputeWindow) {
        return createDisputeWindowValue;
    }

    function getCreatedisputeWindowIdValue() public returns(uint256) {
        return createdisputeWindowIdValue;
    }

    function setCreateDisputeWindowValue(IDisputeWindow _disputeWindowValue) public {
        createDisputeWindowValue = _disputeWindowValue;
    }

    function createDisputeWindow(IController _controller, IUniverse _universe, uint256 _disputeWindowId) public returns (IDisputeWindow) {
        createDisputeWindowUniverseValue = _universe;
        createdisputeWindowIdValue = _disputeWindowId;
        return createDisputeWindowValue;
    }
}
