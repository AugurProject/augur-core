pragma solidity 0.4.20;

import 'external/MkrPriceFeed/DSAuth.sol';
import 'external/MkrPriceFeed/DSNote.sol';
import 'external/MkrPriceFeed/DSMath.sol';


contract DSThing is DSAuth, DSNote, DSMath {

    function S(string s) internal pure returns (bytes4) {
        return bytes4(keccak256(s));
    }

}
