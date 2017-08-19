pragma solidity ^0.4.13;

import 'ROOT/Controller.sol';


// DEPRECATED: Use libraries/ReentrancyGuard.sol
contract Mutex is Controlled {
    bool public mutex = false;

    function acquire() public onlyWhitelistedCallers returns(bool) {
        require(!mutex);
        mutex = true;
        return true;
    }

    function release() public onlyWhitelistedCallers returns(bool) {
        require(mutex);
        mutex = false;
        return true;
    }
}
