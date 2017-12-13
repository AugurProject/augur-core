pragma solidity 0.4.18;


import 'IController.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReputationToken.sol';


contract MockFeeWindowFactory {
    IUniverse private createFeeWindowUniverseValue;
    IFeeWindow private createFeeWindowValue;

    function getCreateFeeWindowUniverseValue() public returns(IUniverse) {
        return createFeeWindowUniverseValue;
    }

    function setCreateFeeWindowValue(IFeeWindow _feeWindowValue) public {
        createFeeWindowValue = _feeWindowValue;
    }

    function createFeeWindow(IController _controller, IUniverse _universe, uint256 _feeWindowId) public returns (IFeeWindow) {
        createFeeWindowUniverseValue = _universe;
        return createFeeWindowValue;
    }
}
