pragma solidity ^0.4.13;

import 'ROOT/Controlled.sol';


contract Register is Controlled {
    event Registration(address indexed sender, uint256 timestamp);

    function register() constant public returns (bool) {
        Registration(msg.sender, block.timestamp);
        return true;
    }
}
