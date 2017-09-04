pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/IController.sol';


// FIXME: remove once this can be imported as a solidty contract
contract Stack {
    function initialize();
}


contract StackFactory {
    function createStack(IController _controller) returns (Stack) {
        Delegator _delegator = new Delegator(_controller, "stack");
        Stack _stack = Stack(_delegator);
        _stack.initialize();
        return _stack;
    }
}
