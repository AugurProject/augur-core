pragma solidity ^0.4.13;


library Bytes20Arrays {
    /*
     * @dev Returns a slice of the array
     * @param self The array to make a slice from.
     * @param start The index to start at.
     * @param size The target number of elements to return in the slice
     * @return A newly allocated slice containing the requested elements
     */
    function slice(bytes20[] _self, uint256 _start, uint256 _size) internal returns (bytes20[]) {
        uint256 _targetSize = _size;
        if (_start >= _self.length) {
            return new bytes20[](0);
        }
        uint256 _maxSize = _self.length - _start;
        if (_maxSize < _targetSize) {
            _targetSize = _maxSize;
        }
        bytes20[] memory _retval = new bytes20[](_targetSize);
        for (uint8 _index; _index < _targetSize; _index++) {
            _retval[_index] = _self[_start + _index];
        }
        return _retval;
    }
}
