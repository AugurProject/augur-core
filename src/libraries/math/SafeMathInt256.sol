pragma solidity ^0.4.13;


/**
 * @title SafeMathInt256
 * @dev Int256 math operations with safety checks that throw on error
 */
library SafeMathInt256 {
    function mul(int256 a, int256 b) internal constant returns (int256) {
        int256 c = a * b;
        require(a == 0 || c / a == b);
        return c;
    }

    function div(int256 a, int256 b) internal constant returns (int256) {
        int256 c = a / b;
        return c;
    }

    function sub(int256 a, int256 b) internal constant returns (int256) {
        require(b <= a);
        return a - b;
    }

    function add(int256 a, int256 b) internal constant returns (int256) {
        int256 c = a + b;
        require(c >= a);
        return c;
    }
}
