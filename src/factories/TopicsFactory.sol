pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/Controller.sol';
import 'ROOT/trading/Topics.sol';


contract TopicsFactory {
    function createTopics(Controller _controller) returns (Topics) {
        Delegator _delegator = new Delegator(_controller, "Topics");
        Topics _topics = Topics(_delegator);
        _topics.initialize(_controller);
        return _topics;
    }
}
