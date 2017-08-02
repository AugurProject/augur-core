pragma solidity ^0.4.13;

import 'ROOT/Controller.sol';
import 'ROOT/libraries/DelegationTarget.sol';
import 'ROOT/libraries/token/ERC20.sol';
import 'ROOT/libraries/token/StandardToken.sol';


contract Branch {
    function getParentBranch() public returns (Branch);
    function getReputationToken() public returns (ReputationToken);
    function isParentOf(Branch _branch) public returns (bool);
    function isContainerForReportingWindow(address _shadyReportingWindow) public returns (bool);
    function isContainerForRegistrationToken(address _shadyRegistrationToken) public returns (bool);
    function isContainerForMarket(address _shadyMarket) public returns (bool);
    function isContainerForReportingToken(address _shadyReportingToken) public returns (bool);
}


contract ReputationToken is DelegationTarget, StandardToken {
    using SafeMath for uint256;

    // Delegation targets do not have their storage updated with values declared here
    // We set them in the initialize function instead
    string public name;
    string public symbol;
    uint256 public decimals;
    Branch public branch;
    ReputationToken public topMigrationDestination;

    function initialize(Branch _branch) public returns (bool) {
        require(_branch != address(0));
        require(branch == address(0));
        branch = _branch;
        name = "Reputation";
        symbol = "REP";
        decimals = 18;
        // FIXME: DELETE THIS BEFORE LAUNCH
        var _reputationFaucet = controller.lookup("reputationFaucet");
        balances[_reputationFaucet] = balances[_reputationFaucet].uint256Add(1000000 ether);
        totalSupply = totalSupply.uint256Add(1000000 ether);
        return true;
    }

    // AUDIT: check for reentrancy issues here, _destination will be called as contracts during validation
    function migrateOut(ReputationToken _destination, address _reporter, uint256 _attotokens) public returns (bool) {
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

    function migrateIn(address _reporter, uint256 _attotokens) public returns (bool) {
        require(ReputationToken(msg.sender) == branch.getParentBranch().getReputationToken());
        balances[_reporter] = balances[_reporter].uint256Add(_attotokens);
        totalSupply = totalSupply.uint256Add(_attotokens);
        return true;
    }

    function migrateFromLegacyRepContract() public returns (bool) {
        var _legacyRepToken = ERC20(controller.lookup("legacyRepContract"));
        var _legacyBalance = _legacyRepToken.balanceOf(msg.sender);
        _legacyRepToken.transferFrom(msg.sender, address(0), _legacyBalance);
        balances[msg.sender] = balances[msg.sender].uint256Add(_legacyBalance);
        totalSupply = totalSupply.uint256Add(_legacyBalance);
        return true;
    }

    // AUDIT: check for reentrancy issues here, _source and _destination will be called as contracts during validation
    function trustedTransfer(address _source, address _destination, uint256 _attotokens) public returns (bool) {
        require(branch.isContainerForReportingWindow(msg.sender) || branch.isContainerForRegistrationToken(msg.sender) || branch.isContainerForMarket(msg.sender) || branch.isContainerForReportingToken(msg.sender));
        balances[_source] = balances[_source].uint256Sub(_attotokens);
        balances[_destination] = balances[_destination].uint256Add(_attotokens);
        totalSupply = totalSupply.uint256Add(_attotokens);
        Transfer(_source, _destination, _attotokens);
        return true;
    }

    function assertReputationTokenIsLegit(ReputationToken _shadyReputationToken) private returns (bool) {
        var _shadyBranch = _shadyReputationToken.branch();
        require(branch.isParentOf(_shadyBranch));
        var _legitBranch = _shadyBranch;
        require(_legitBranch.getReputationToken() == _shadyReputationToken);
        return true;
    }
}
