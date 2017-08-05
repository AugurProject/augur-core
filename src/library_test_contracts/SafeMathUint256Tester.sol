pragma solidity ^0.4.13;

import 'ROOT/libraries/math/SafeMathUint256.sol';


contract SafeMathUint256Tester {
    function initialize() public constant {
    }

    function mul(uint256 _a, uint256 _b) internal constant returns (uint256) {
        return SafeMathUint256.mul(_a, _b);
    }

    function div(uint256 _a, uint256 _b) internal constant returns (uint256) {
        return SafeMathUint256.div(_a, _b);
    }

    function sub(uint256 _a, uint256 _b) internal constant returns (uint256) {
        return SafeMathUint256.sub(_a, _b);
    }

    function add(uint256 _a, uint256 _b) public constant returns (uint256) {
        return SafeMathUint256.add(_a, _b);
    }

    function min(uint256 _a, uint256 _b) public constant returns (uint256) {
        return SafeMathUint256.min(_a, _b);
    }

    function max(uint256 _a, uint256 _b) public constant returns (uint256) {
        return SafeMathUint256.max(_a, _b);
    }
}