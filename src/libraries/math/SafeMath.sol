pragma solidity ^0.4.13;


/**
 * @title SafeMath
 * @dev Math operations with safety checks that throw on error
 */
library SafeMath {
    function int256Mul(int256 a, int256 b) internal constant returns (int256) {
        int256 c = a * b;
        require(a == 0 || c / a == b);
        return c;
    }

    function int256Div(int256 a, int256 b) internal constant returns (int256) {
        // assert(b > 0); // Solidity automatically throws when dividing by 0
        int256 c = a / b;
        // assert(a == b * c + a % b); // There is no case in which this doesn't hold
        return c;
    }

    function int256Sub(int256 a, int256 b) internal constant returns (int256) {
        require(b <= a);
        return a - b;
    }

    function adint256Add(int256 a, int256 b) internal constant returns (int256) {
        int256 c = a + b;
        require(c >= a);
        return c;
    }

    function uint256Mul(uint256 a, uint256 b) internal constant returns (uint256) {
        uint256 c = a * b;
        require(a == 0 || c / a == b);
        return c;
    }

    function uint256Div(uint256 a, uint256 b) internal constant returns (uint256) {
        // assert(b > 0); // Solidity automatically throws when dividing by 0
        uint256 c = a / b;
        // assert(a == b * c + a % b); // There is no case in which this doesn't hold
        return c;
    }

    function uint256Sub(uint256 a, uint256 b) internal constant returns (uint256) {
        require(b <= a);
        return a - b;
    }

    function uint256Add(uint256 a, uint256 b) internal constant returns (uint256) {
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
}
