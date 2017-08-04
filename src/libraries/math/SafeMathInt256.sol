pragma solidity ^0.4.13;


/**
 * @title SafeMathInt256
 * @dev Int256 math operations with safety checks that throw on error
 */
library SafeMathInt256 {
    // Signed ints with n bits can range from -2**(n-1) to (2**(n-1) - 1)
    int256 private constant INT256_MIN = -2**(255);
    int256 private constant INT256_MAX = (2**(255) - 1);

    function getInt256Min() public constant returns (int256) {
        return INT256_MIN;
    }

    function getInt256Max() public constant returns (int256) {
        return INT256_MAX;
    }

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
        require(((a >= 0) && (b >= a - INT256_MAX)) || ((a < 0) && (b <= a - INT256_MIN)));
        return a - b;
    }

    function add(int256 a, int256 b) internal constant returns (int256) {
        int256 c = a + b;
        require(c >= a && c >= b);
        return c;
    }
}
