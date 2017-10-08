pragma solidity 0.4.17;
pragma experimental ABIEncoderV2;
pragma experimental "v0.5.0";


library RunningAverage {
    struct Data {
        uint256 sum;
        uint128 count;
    }

    function currentAverage(Data storage _this) internal returns (uint256) {
        return _this.sum / _this.count;
    }

    function record(Data storage _this, uint256 _input) internal returns (bool) {
        _this.count++;
        _this.sum += _input;
        return true;
    }
}
