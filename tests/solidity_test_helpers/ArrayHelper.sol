pragma solidity ^0.4.13;

import 'ROOT/libraries/arrays/Uint256Arrays.sol';


contract ArrayHelper {
    using Uint256Arrays for uint256[];

    uint256[] data;

    function setData(uint256[] _data) public returns (bool) {
        data = _data;
        return true;
    }

    function getSize() constant public returns (uint256) {
        return data.length;
    }

    function getItem(uint256 _index) constant public returns (uint256) {
        return data[_index];
    }

    function getSlice(uint256 _start, uint256 _num) constant public returns (uint256[]) {
        return data.slice(_start, _num);
    }
}
