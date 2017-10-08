pragma solidity 0.4.17;
pragma experimental ABIEncoderV2;
pragma experimental "v0.5.0";

import 'Controlled.sol';


contract Register is Controlled {
    event Registration(address indexed sender, uint256 timestamp);

    function register() public returns (bool) {
        Registration(msg.sender, block.timestamp);
        return true;
    }
}
