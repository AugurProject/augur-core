pragma solidity ^0.4.13;

import 'libraries/Typed.sol';
import 'libraries/token/ERC20.sol';
import 'reporting/IBranch.sol';


contract IReputationToken is Typed, ERC20 {
    function initialize(IBranch _branch) public returns (bool);
    function migrateOut(IReputationToken _destination, address _reporter, uint256 _attotokens) public returns (bool);
    function migrateIn(address _reporter, uint256 _attotokens) public returns (bool);
    function trustedTransfer(address _source, address _destination, uint256 _attotokens) public returns (bool);
    function getBranch() constant returns (IBranch);
    function getTopMigrationDestination() constant returns (IReputationToken);
}
