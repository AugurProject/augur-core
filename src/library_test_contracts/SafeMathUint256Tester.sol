pragma solidity ^0.4.13;

import 'ROOT/libraries/math/SafeMathUint256.sol';


contract SafeMathUint256Tester {
    using SafeMathUint256 for uint256;

    function initialize() public constant {
    }

    function mul(uint256 _a, uint256 _b) internal constant returns (uint256) {
        return _a.mul(_b);
    }

    function div(uint256 _a, uint256 _b) internal constant returns (uint256) {
        return _a.div(_b);
    }

    function sub(uint256 _a, uint256 _b) internal constant returns (uint256) {
        return _a.sub(_b);
    }

    function add(uint256 _a, uint256 _b) public constant returns (uint256) {
        return _a.add(_b);
    }

    function min() {
        
    }

    function max() {
        
    }
}