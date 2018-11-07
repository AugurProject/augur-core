pragma solidity 0.4.24;


import 'libraries/CloneFactory.sol';
import 'IController.sol';
import 'TEST/DelegatorHelper.sol';


contract DelegatorHelperFactory is CloneFactory {
    function createDelegatorHelper(IController _controller) public payable returns (DelegatorHelper) {
        return DelegatorHelper(createClone(_controller.lookup("DelegatorHelper")));
    }
}
