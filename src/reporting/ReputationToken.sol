pragma solidity ^0.4.13;

import 'ROOT/libraries/DelegationTarget.sol';
import 'ROOT/libraries/Typed.sol';
import 'ROOT/libraries/Initializable.sol';
import 'ROOT/libraries/token/ERC20.sol';
import 'ROOT/libraries/token/StandardToken.sol';
import 'ROOT/reporting/Interfaces.sol';


contract ReputationToken is DelegationTarget, Typed, Initializable, StandardToken, IReputationToken {
    using SafeMath for uint256;

    string public name;
    string public symbol;
    uint256 public decimals;
    IBranch private branch;
    IReputationToken private topMigrationDestination;

    function initialize(IBranch _branch) public beforeInitialized returns (bool) {
        endInitialization();
        require(_branch != address(0));
        branch = _branch;
        name = "Reputation";
        symbol = "REP";
        decimals = 18;
        // FIXME: DELETE THIS BEFORE LAUNCH
        var _reputationFaucet = controller.lookup("ReputationFaucet");
        balances[_reputationFaucet] = balances[_reputationFaucet].add(1000000 ether);
        totalSupply = totalSupply.add(1000000 ether);
        return true;
    }

    // AUDIT: check for reentrancy issues here, _destination will be called as contracts during validation
    function migrateOut(IReputationToken _destination, address _reporter, uint256 _attotokens) public afterInitialized returns (bool) {
        assertReputationTokenIsLegit(_destination);
        if (msg.sender != _reporter) {
            allowed[_reporter][msg.sender] = allowed[_reporter][msg.sender].uint256Sub(_attotokens);
        }
        balances[_reporter] = balances[_reporter].uint256Sub(_attotokens);
        totalSupply = totalSupply.uint256Sub(_attotokens);
        _destination.migrateIn(_reporter, _attotokens);
        if (topMigrationDestination == address(0) || _destination.totalSupply() > topMigrationDestination.totalSupply()) {
            topMigrationDestination = _destination;
        }
        return true;
    }

<<<<<<< HEAD
    function migrateIn(address _reporter, uint256 _attotokens) public returns (bool) {
        require(ReputationToken(msg.sender) == branch.getParentBranch().getReputationToken());
        balances[_reporter] = balances[_reporter].uint256Add(_attotokens);
        totalSupply = totalSupply.uint256Add(_attotokens);
=======
    function migrateIn(address _reporter, uint256 _attotokens) public afterInitialized returns (bool) {
        require(IReputationToken(msg.sender) == branch.getParentBranch().getReputationToken());
        balances[_reporter] = balances[_reporter].add(_attotokens);
        totalSupply = totalSupply.add(_attotokens);
>>>>>>> 9868ad75e9f47e9802823110aed19f310f0f1703
        return true;
    }

    function migrateFromLegacyRepContract() public afterInitialized returns (bool) {
        var _legacyRepToken = ERC20(controller.lookup("legacyRepContract"));
        var _legacyBalance = _legacyRepToken.balanceOf(msg.sender);
        _legacyRepToken.transferFrom(msg.sender, address(0), _legacyBalance);
        balances[msg.sender] = balances[msg.sender].uint256Add(_legacyBalance);
        totalSupply = totalSupply.uint256Add(_legacyBalance);
        return true;
    }

    // AUDIT: check for reentrancy issues here, _source and _destination will be called as contracts during validation
<<<<<<< HEAD
    function trustedTransfer(address _source, address _destination, uint256 _attotokens) public returns (bool) {
        require(branch.isContainerForReportingWindow(msg.sender) || branch.isContainerForRegistrationToken(msg.sender) || branch.isContainerForMarket(msg.sender) || branch.isContainerForReportingToken(msg.sender));
        balances[_source] = balances[_source].uint256Sub(_attotokens);
        balances[_destination] = balances[_destination].uint256Add(_attotokens);
        totalSupply = totalSupply.uint256Add(_attotokens);
=======
    function trustedTransfer(address _source, address _destination, uint256 _attotokens) public afterInitialized returns (bool) {
        Typed _caller = Typed(msg.sender);
        require(branch.isContainerForReportingWindow(_caller) || branch.isContainerForRegistrationToken(_caller) || branch.isContainerForMarket(_caller) || branch.isContainerForReportingToken(_caller));
        balances[_source] = balances[_source].sub(_attotokens);
        balances[_destination] = balances[_destination].add(_attotokens);
        totalSupply = totalSupply.add(_attotokens);
>>>>>>> 9868ad75e9f47e9802823110aed19f310f0f1703
        Transfer(_source, _destination, _attotokens);
        return true;
    }

    function assertReputationTokenIsLegit(IReputationToken _shadyReputationToken) private returns (bool) {
        var _shadyBranch = _shadyReputationToken.getBranch();
        require(branch.isParentOf(_shadyBranch));
        var _legitBranch = _shadyBranch;
        require(_legitBranch.getReputationToken() == _shadyReputationToken);
        return true;
    }

    function getTypeName() constant returns (bytes32) {
        return "ReputationToken";
    }

    function getBranch() constant returns (IBranch) {
        return branch;
    }

    function getTopMigrationDestination() constant returns (IReputationToken) {
        return topMigrationDestination;
    }
}
