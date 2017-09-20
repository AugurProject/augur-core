pragma solidity ^0.4.13;

import 'ROOT/Controlled.sol';
import 'ROOT/libraries/token/StandardToken.sol';


// AUDIT/CONSIDER: Is it better that this contract provide generic functions that are limited to whitelisted callers or for it to have many specific functions which have more limited and specific validation?
contract Augur is Controlled {
    function trustedTransfer(StandardToken _token, address _from, address _to, uint256 _amount) public onlyWhitelistedCallers returns (bool) {
        require(_amount > 0);
        _token.transferFrom(_from, _to, _amount);
        return true;
    }
}
