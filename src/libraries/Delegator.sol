pragma solidity ^0.4.13;

import 'ROOT/Controller.sol';
import 'ROOT/libraries/DelegationTarget.sol';


contract Delegator is DelegationTarget {
    function Delegator(Controller _controller, bytes32 _controllerLookupName) {
        controller = _controller;
        controllerLookupName = _controllerLookupName;
    }

    // We currently only support a single non-array return value
    // If we truly need to return more advanced sets of data we could follow
    // the pattern demonstrated here: https://gist.github.com/Arachnid/4ca9da48d51e23e5cfe0f0e14dd6318f
    // But in a way that is automated.
    function() payable {
        // Do nothing if we haven't properly set up the delegator to delegate calls
        if (controllerLookupName == 0) {
            return;
        }

        // Get the delegation target contract
        address _target = controller.lookup(controllerLookupName);

        assembly {
            //0x40 is the address where the next free memory slot is stored in Solidity
            let _calldataMemoryOffset := mload(0x40)
            // Update the pointer at 0x40 to point at new free memory location so any theoretical allocation doesn't stomp our memory in this call
            let _size := 0
            switch gt(calldatasize, 32)
            case 1 {
                _size := calldatasize
            } default {
                _size := 32
            }
            mstore(0x40, add(_calldataMemoryOffset, _size))
            // Copy method signature and parameters of this call into memory
            calldatacopy(_calldataMemoryOffset, 0x0, calldatasize)
            // Call the actual method via delegation and store the result at offset _calldataMemoryOffset assuming size of 32
            let _retval := delegatecall(gas, _target, _calldataMemoryOffset, calldatasize, _calldataMemoryOffset, 32)
            switch _retval
            case 0 {
                // 0 == it threw, so we revert
                revert(0,0)
            } default {
                // If the call succeeded return the data in mem[_calldataMemoryOffset..32]
                return(_calldataMemoryOffset, 32)
            }
        }
    }
}
