pragma solidity ^0.4.13;

import 'ROOT/Controller.sol';
import 'ROOT/libraries/DelegationTarget.sol';

contract Delegator is DelegationTarget{

    function Delegator(address controllerAddress, bytes32 keyVal) {
        controller = Controller(controllerAddress);
        controllerLookupName = keyVal;
    }

    // We currently only support a single non-array return value
    // If we truly need to return more advanced sets of data we could follow
    // the pattern demonstrated here: https://gist.github.com/Arachnid/4ca9da48d51e23e5cfe0f0e14dd6318f
    function() payable {
        // Do nothing if we haven't properly set up the delegator to delegate calls
        if (controllerLookupName == 0) {
            return;
        }

        // Get the delegation target contract
        address target = controller.lookup(controllerLookupName);

        assembly {
            let o_code := mload(0x40) //Memory end
            // Copy method signature and parameters of this call into memory
            calldatacopy(o_code, 0x0, calldatasize)
            // Call the actual method via delegation and store the result at offset o_code assuming size of 32
            let retval := delegatecall(sub(gas, 10000), target, o_code, calldatasize, o_code, 32)
            // 0 == it threw, so we do so as well by jumping to bad destination (02)
            jumpi(0x02, iszero(retval))
            // Return the data in mem[o_code..32]
            return(o_code, 32)
        }
    }
}