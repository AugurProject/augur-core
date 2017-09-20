pragma solidity ^0.4.13;

import 'ROOT/Controlled.sol';
import 'ROOT/libraries/token/StandardToken.sol';


contract Augur is Controlled {
    function trustedTransfer(StandardToken _token, address _from, address _to, uint256 _amount) public onlyWhitelistedCallers returns (bool) {
        require(_amount > 0);
        _token.transferFrom(_from, _to, _amount);
        return true;
    }
}
