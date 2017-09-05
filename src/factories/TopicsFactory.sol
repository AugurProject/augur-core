pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/IController.sol';
import 'ROOT/trading/ITopics.sol';


contract TopicsFactory {
    function createTopics(IController _controller) returns (ITopics) {
        Delegator _delegator = new Delegator(_controller, "Topics");
        ITopics _topics = ITopics(_delegator);
        _topics.initialize(_controller);
        return _topics;
    }
}
