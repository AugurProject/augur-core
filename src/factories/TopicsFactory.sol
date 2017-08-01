pragma solidity ^0.4.11;

import 'ROOT/libraries/Delegator.sol';


// FIXME: remove once this can be imported as a solidty contract
contract Topics {
    function initialize();
}


contract TopicsFactory {

    function createTopics(address controller) returns (Topics) {
        Delegator del = new Delegator(controller, "topics");
        Topics topics = Topics(del);
        topics.initialize();
        return topics;
    }
}