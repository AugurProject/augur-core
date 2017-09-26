pragma solidity ^0.4.13;


library Bytes32Arrays {
    /*
     * @dev Returns a slice of the array
     * @param self The array to make a slice from.
     * @param start The index to start at.
     * @param size The target number of elements to return in the slice
     * @return A newly allocated slice containing the requested elements
     */
    function slice(bytes32[] _self, uint256 _start, uint256 _size) internal returns (bytes32[]) {
        uint256 _targetSize = _size;
        if (_start >= _self.length) {
            return new bytes32[](0);
        }
        uint256 _maxSize = _self.length - _start;
        if (_maxSize < _targetSize) {
            _targetSize = _maxSize;
        }
        bytes32[] memory _retval = new bytes32[](_targetSize);
        for (uint8 _index; _index < _targetSize; _index++) {
            _retval[_index] = _self[_start + _index];
        }
        return _retval;
    }
}
