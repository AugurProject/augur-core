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


contract IIterableMap {
    function initialize(address _owner) public returns (bool);
    function add(bytes32, uint256) public returns (bool);
    function update(bytes32, uint256) public returns (bool);
    function addOrUpdate(bytes32, uint256) public returns (bool);
    function remove(bytes32) public returns (bool);
    function getByKeyOrZero(bytes32) public constant returns (uint256);
    function getByKey(bytes32) public constant returns (uint256);
    function getByOffset(uint256) public constant returns (bytes32);
    function contains(bytes32) public constant returns (bool);
    function count() public constant returns (uint256);
}
