pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/Controller.sol';
import 'ROOT/reporting/Interfaces.sol';


contract TopicsFactory {
    function createTopics(Controller _controller) returns (ITopics) {
        Delegator _delegator = new Delegator(_controller, "topics");
        ITopics _topics = ITopics(_delegator);
        _topics.initialize();
        return _topics;
    }
}
