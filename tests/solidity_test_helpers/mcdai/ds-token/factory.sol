pragma solidity ^0.4.18;

import "./token.sol";

contract DSTokenFactory {
    event LogMake(address indexed owner, address token);

    function make(
        bytes32 symbol, bytes32 name
    ) public returns (DSToken result) {
        result = new DSToken(symbol);
        result.setName(name);
        result.setOwner(msg.sender);
        emit LogMake(msg.sender, result);
    }
}
