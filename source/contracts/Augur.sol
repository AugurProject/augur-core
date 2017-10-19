pragma solidity 0.4.17;


import 'Controlled.sol';
import 'libraries/token/ERC20.sol';
import 'reporting/IUniverse.sol';


// AUDIT/CONSIDER: Is it better that this contract provide generic functions that are limited to whitelisted callers or for it to have many specific functions which have more limited and specific validation?
contract Augur is Controlled {
    event UniverseCreated(IUniverse universe, IUniverse indexed parentUniverse, bytes32 parentPayoutDistributionHash);

    function trustedTransfer(ERC20 _token, address _from, address _to, uint256 _amount) public onlyWhitelistedCallers returns (bool) {
        require(_amount > 0);
        _token.transferFrom(_from, _to, _amount);
        return true;
    }

    function logUniverseCreated(IUniverse _universe, IUniverse _parentUniverse, bytes32 _parentPayoutDistributionHash) public onlyWhitelistedCallers returns (bool) {
        UniverseCreated(_universe, _parentUniverse, _parentPayoutDistributionHash);
        return true;
    }
}
