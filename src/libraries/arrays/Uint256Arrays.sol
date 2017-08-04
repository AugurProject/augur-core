pragma solidity ^0.4.13;


library Uint256Arrays {
    /*
     * @dev Returns a slice of the array
     * @param self The array to make a slice from.
     * @param start The index to start at.
     * @param size The target number of elements to return in the slice
     * @return A newly allocated slice containing the requested elements
     */
    function slice(uint256[] _self, uint256 _start, uint256 _size) internal returns (uint256[]) {
        uint256 _targetSize = _size;
        if (_start >= _self.length) {
            return new uint256[](0);
        }
        uint256 _maxSize = _self.length - _start;
        if (_maxSize < _targetSize) {
            _targetSize = _maxSize;
        }
        uint256 _index = 0;
        uint256[] memory _retval = new uint256[](_targetSize);
        while (_index < _targetSize) {
            _retval[_index] = _self[_start + _index];
            _index++;
        }
        return _retval;

    }
}
