pragma solidity ^0.4.13;

import 'ROOT/Controller.sol';
import 'ROOT/libraries/DelegationTarget.sol';


contract Delegator is DelegationTarget {
    function Delegator(address _controller, bytes32 _controllerLookupName) {
        controller = Controller(_controller);
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
            let _o_code := mload(0x40) //0x40 is the address where the next free memory slot is stored in Solidity
            // Copy method signature and parameters of this call into memory
            calldatacopy(_o_code, 0x0, calldatasize)
            // Call the actual method via delegation and store the result at offset o_code assuming size of 32
            let _retval := delegatecall(sub(gas, 10000), _target, _o_code, calldatasize, _o_code, 32)
            // 0 == it threw, so we do so as well by jumping to bad destination (02)
            jumpi(0x02, iszero(_retval))
            // Return the data in mem[o_code..32]
            return(_o_code, 32)
        }
    }
}