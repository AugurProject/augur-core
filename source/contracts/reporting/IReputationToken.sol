pragma solidity 0.4.17;


import 'libraries/Typed.sol';
import 'libraries/token/ERC20.sol';
import 'reporting/IUniverse.sol';


contract IReputationToken is Typed, ERC20 {
    function initialize(IUniverse _universe) public returns (bool);
    function migrateOut(IReputationToken _destination, address _reporter, uint256 _attotokens) public returns (bool);
    function migrateIn(address _reporter, uint256 _attotokens) public returns (bool);
    function mintForDisputeBondMigration(uint256 _amount) public afterInitialized returns (bool);
    function trustedTransfer(address _source, address _destination, uint256 _attotokens) public returns (bool);
    function getUniverse() public view returns (IUniverse);
    function getTopMigrationDestination() public view returns (IReputationToken);
}
