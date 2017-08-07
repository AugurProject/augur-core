pragma solidity ^0.4.13;

import 'ROOT/libraries/math/SafeMathInt256.sol';


contract SafeMathInt256Tester {
    function initialize() public constant {
    }

    function mul(int256 _a, int256 _b) public constant returns (int256) {
        return SafeMathInt256.mul(_a, _b);
    }

    function div(int256 _a, int256 _b) public constant returns (int256) {
        return SafeMathInt256.div(_a, _b);
    }

    function sub(int256 _a, int256 _b) public constant returns (int256) {
        return SafeMathInt256.sub(_a, _b);
    }

    function add(int256 _a, int256 _b) public constant returns (int256) {
        return SafeMathInt256.add(_a, _b);
    }

    function min(int256 _a, int256 _b) public constant returns (int256) {
        return SafeMathInt256.min(_a, _b);
    }

    function max(int256 _a, int256 _b) public constant returns (int256) {
        return SafeMathInt256.max(_a, _b);
    }

    function getInt256Min() public constant returns (int256) {
        return SafeMathInt256.getInt256Min();
    }

    function getInt256Max() public constant returns (int256) {
        return SafeMathInt256.getInt256Max();
    }
}