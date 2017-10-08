pragma solidity 0.4.17;


import 'Controlled.sol';


contract Register is Controlled {
    event Registration(address indexed sender, uint256 timestamp);

    function register() public returns (bool) {
        Registration(msg.sender, block.timestamp);
        return true;
    }
}
