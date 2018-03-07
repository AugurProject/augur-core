pragma solidity 0.4.20;

import 'libraries/math/SafeMathUint256.sol';


library RunningAverage {
    using SafeMathUint256 for uint256;

    struct Data {
        uint256 sum;
        uint128 count;
    }

    function currentAverage(Data storage _this) internal view returns (uint256) {
        return _this.sum.div(_this.count);
    }

    function record(Data storage _this, uint256 _input) internal returns (bool) {
        _this.count++;
        _this.sum += _input;
        return true;
    }
}
