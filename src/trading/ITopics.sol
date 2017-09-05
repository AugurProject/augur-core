pragma solidity ^0.4.13;

import 'ROOT/IController.sol';


contract ITopics {
    function initialize(IController) public returns (bool);
    function updatePopularity(bytes32 topic, uint256 amount) public returns (bool);
    function getPopularity(bytes32 topic) constant returns (uint256);
    function getTopicByOffset(uint256 offset) constant returns (bytes32);
    function getPopularityByOffset(uint256 offset) constant returns (uint256);
    function count() constant returns (uint256);
}
