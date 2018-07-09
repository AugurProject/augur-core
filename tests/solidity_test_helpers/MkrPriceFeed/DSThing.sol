pragma solidity 0.4.20;

import 'TEST/MkrPriceFeed/DSAuth.sol';
import 'TEST/MkrPriceFeed/DSNote.sol';
import 'TEST/MkrPriceFeed/DSMath.sol';


contract DSThing is DSAuth, DSNote, DSMath {

    function S(string s) internal pure returns (bytes4) {
        return bytes4(keccak256(s));
    }

}