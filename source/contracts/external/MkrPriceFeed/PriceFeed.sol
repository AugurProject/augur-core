pragma solidity 0.4.20;

import 'external/MkrPriceFeed/DSThing.sol';


contract PriceFeed is DSThing {

    uint128 val;
    uint32 public zzz;

    function peek() public view
        returns (bytes32,bool)
    {
        return (bytes32(val), now < zzz);
    }

    function read() public view
        returns (bytes32)
    {
        assert(now < zzz);
        return bytes32(val);
    }

    function post(uint128 val_, uint32 zzz_, address med_) public note auth {
        val = val_;
        zzz = zzz_;
        bool ret = med_.call(bytes4(keccak256("poke()")));
        ret;
    }

    function void() public note auth {
        zzz = 0;
    }

}
