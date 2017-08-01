pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/Controller.sol';


// FIXME: remove once this can be imported as a solidty contract
contract Topics {
    function initialize();
}


contract TopicsFactory {
    function createTopics(Controller _controller) returns (Topics) {
        Delegator _delegator = new Delegator(_controller, "topics");
        Topics _topics = Topics(_delegator);
        _topics.initialize();
        return _topics;
    }
}