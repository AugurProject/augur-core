pragma solidity 0.4.20;

import 'external/MkrPriceFeed/DSGuard.sol';


contract DSGuardFactory {
    mapping (address => bool)  public  isGuard;

    function newGuard() public returns (DSGuard guard) {
        guard = new DSGuard();
        guard.setOwner(msg.sender);
        isGuard[guard] = true;
    }
}
