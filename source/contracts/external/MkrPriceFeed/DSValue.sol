pragma solidity 0.4.20;

import 'external/MkrPriceFeed/DSThing.sol';


contract DSValue is DSThing {
    bool    has;
    bytes32 val;

    function peek() public view returns (bytes32, bool) {
        return (val,has);
    }

    function read() public view returns (bytes32) {
        bytes32 wut;
        bool haz;
        (wut, haz) = peek();
        assert(haz);
        return wut;
    }

    function poke(bytes32 wut) public note auth {
        val = wut;
        has = true;
    }

    function void() public note auth {  // unset the value
        has = false;
    }
}
