pragma solidity 0.4.20;

import 'IController.sol';
import 'libraries/Ownable.sol';


contract EscapeHatchController is Ownable {
    IController public controller;

    function setController(IController _controller) public onlyOwner returns (bool) {
        controller = _controller;
        return true;
    }

    function emergencyStop() public onlyOwner returns (bool) {
        controller.emergencyStop();
        return true;
    }

    function onTransferOwnership(address, address) internal returns (bool) {
        return true;
    }
}