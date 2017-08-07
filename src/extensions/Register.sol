pragma solidity ^0.4.13;

import 'ROOT/Controller.sol';


contract Register is Controlled {
    event Registration(address indexed _sender, uint256 _timestamp);

    function register() constant public returns (bool) {
        Registration(msg.sender, block.timestamp);
        return true;
    }
}