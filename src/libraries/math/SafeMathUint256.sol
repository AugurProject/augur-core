pragma solidity ^0.4.13;


/**
 * @title SafeMathUint256
 * @dev Uint256 math operations with safety checks that throw on error
 */
library SafeMathUint256 {
    function mul(uint256 a, uint256 b) internal constant returns (uint256) {
        require(safeToMultiply(a, b));
        return a * b;
    }

    function div(uint256 a, uint256 b) internal constant returns (uint256) {
        // assert(b > 0); // Solidity automatically throws when dividing by 0
        uint256 c = a / b;
        // assert(a == b * c + a % b); // There is no case in which this doesn't hold
        return c;
    }

    function sub(uint256 a, uint256 b) internal constant returns (uint256) {
        require(b <= a);
        return a - b;
    }

    function add(uint256 a, uint256 b) internal constant returns (uint256) {
        uint256 c = a + b;
        require(c >= a);
        return c;
    }

    function min(uint256 a, uint256 b) internal constant returns (uint256) {
        if (a <= b) {
            return a;
        } else {
            return b;
        }
    }

    function max(uint256 a, uint256 b) internal constant returns (uint256) {
        if (a >= b) {
            return a;
        } else {
            return b;
        }
    }

    function safeToMultiply(uint256 a, uint256 b) internal constant returns (bool) {
        uint256 c = a * b;
        if (a == 0 || c / a == b) {
            return true;
        }
        return false;
    }

    // Float [fixed point] Operations
    function fxpMul(uint256 a, uint256 b) internal constant returns (uint256) {
        require(safeToMultiply(a, b));
        return a * b / 10 ** 18;
    }

    function fxpDiv(uint256 a, uint256 b) internal constant returns (uint256) {
        return a * 10 ** 18 / b;
    }
}
