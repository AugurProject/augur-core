pragma solidity ^0.4.11;

import 'ROOT/libraries/Delegator.sol';

// FIXME: remove once this can be imported as a solidty contract
contract Stack {
    function initialize();
}

contract StackFactory {

    function createStack(address controller) returns (Stack) {
        Delegator del = new Delegator(controller, 'stack');
        Stack stack = Stack(del);
        stack.initialize();
        return stack;
    }
}