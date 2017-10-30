pragma solidity 0.4.17;


import 'libraries/ITyped.sol';
import 'libraries/token/ERC20.sol';
import 'reporting/IUniverse.sol';


contract IReputationToken is ITyped, ERC20 {
    function initialize(IUniverse _universe) public returns (bool);
    function migrateOutStakeToken(IReputationToken _destination, address _reporter, uint256 _attotokens) public returns (bool);
    function migrateOutDisputeBond(IReputationToken _destination, address _reporter, uint256 _attotokens) public returns (bool);
    function migrateOut(IReputationToken _destination, address _reporter, uint256 _attotokens) public returns (bool);
    function migrateIn(address _reporter, uint256 _attotokens, bool _bonusIfInForkWindow) public returns (bool);
    function mintForDisputeBondMigration(uint256 _amount) public returns (bool);
    function trustedReportingWindowTransfer(address _source, address _destination, uint256 _attotokens) public returns (bool);
    function trustedMarketTransfer(address _source, address _destination, uint256 _attotokens) public returns (bool);
    function trustedStakeTokenTransfer(address _source, address _destination, uint256 _attotokens) public returns (bool);
    function trustedParticipationTokenTransfer(address _source, address _destination, uint256 _attotokens) public returns (bool);
    function getUniverse() public view returns (IUniverse);
    function getTopMigrationDestination() public view returns (IReputationToken);
}
