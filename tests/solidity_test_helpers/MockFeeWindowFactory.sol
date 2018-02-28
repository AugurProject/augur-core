pragma solidity 0.4.20;


import 'IController.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IFeeWindow.sol';


contract MockFeeWindowFactory {
    IUniverse private createFeeWindowUniverseValue;
    IFeeWindow private createFeeWindowValue;
    uint256 private createfeeWindowIdValue;

    function getCreateFeeWindowUniverseValue() public returns(IUniverse) {
        return createFeeWindowUniverseValue;
    }

    function getCreateFeeWindowValue(IFeeWindow _feeWindowValue) public returns(IFeeWindow) {
        return createFeeWindowValue;
    }

    function getCreatefeeWindowIdValue() public returns(uint256) {
        return createfeeWindowIdValue;
    }

    function setCreateFeeWindowValue(IFeeWindow _feeWindowValue) public {
        createFeeWindowValue = _feeWindowValue;
    }

    function createFeeWindow(IController _controller, IUniverse _universe, uint256 _feeWindowId) public returns (IFeeWindow) {
        createFeeWindowUniverseValue = _universe;
        createfeeWindowIdValue = _feeWindowId;
        return createFeeWindowValue;
    }
}
