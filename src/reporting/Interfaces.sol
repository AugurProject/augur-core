pragma solidity ^0.4.13;

import 'ROOT/libraries/token/ERC20.sol';
import 'ROOT/libraries/token/VariableSupplyToken.sol';
import 'ROOT/libraries/Typed.sol';
import 'ROOT/reporting/Branch.sol';
import 'ROOT/reporting/Market.sol';
import 'ROOT/reporting/ReportingToken.sol';
import 'ROOT/reporting/ReportingWindow.sol';
import 'ROOT/reporting/DisputeBondToken.sol';
import 'ROOT/reporting/RegistrationToken.sol';


contract IShareToken is ERC20, Typed {
    function initialize(Market _market, uint8 _outcome) public returns (bool);
    function getMarket() constant returns (Market);
    function balanceOf(address) constant returns (uint256);
    function transfer(address, uint256) returns (bool);
    function transferFrom(address, address, uint256) returns (bool);
    function destroyShares(address, uint256 balance) public;
    function getOutcome() public constant returns (uint8);
}


contract ITopics {
    function initialize() public returns (bool);
    function updatePopularity(bytes32 topic, uint256 amount) public returns (bool);
    function getPopularity(bytes32 topic) constant returns (uint256);
    function getTopicByOffset(uint256 offset) constant returns (bytes32);
    function getPopularityByOffset(uint256 offset) constant returns (uint256);
    function count() constant returns (uint256);
}
