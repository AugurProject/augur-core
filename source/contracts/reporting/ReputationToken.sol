pragma solidity 0.4.17;


import 'reporting/IReputationToken.sol';
import 'libraries/DelegationTarget.sol';
import 'libraries/ITyped.sol';
import 'libraries/Initializable.sol';
import 'libraries/token/VariableSupplyToken.sol';
import 'libraries/token/ERC20.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IMarket.sol';
import 'reporting/Reporting.sol';
import 'libraries/math/SafeMathUint256.sol';


contract ReputationToken is DelegationTarget, ITyped, Initializable, VariableSupplyToken, IReputationToken {
    using SafeMathUint256 for uint256;

    //FIXME: Delegated contracts cannot currently use string values, so we will need to find a workaround if this hasn't been fixed before we release
    string constant public name = "Reputation";
    string constant public symbol = "REP";
    uint256 constant public decimals = 18;
    IUniverse private universe;
    IReputationToken private topMigrationDestination;

    function initialize(IUniverse _universe) public beforeInitialized returns (bool) {
        endInitialization();
        require(_universe != address(0));
        universe = _universe;
        return true;
    }

    // AUDIT: check for reentrancy issues here, _destination will be called as contracts during validation
    function migrateOut(IReputationToken _destination, address _reporter, uint256 _attotokens) public afterInitialized returns (bool) {
        assertReputationTokenIsLegit(_destination);
        if (msg.sender != _reporter) {
            allowed[_reporter][msg.sender] = allowed[_reporter][msg.sender].sub(_attotokens);
        }
        balances[_reporter] = balances[_reporter].sub(_attotokens);
        supply = supply.sub(_attotokens);
        _destination.migrateIn(_reporter, _attotokens);
        if (topMigrationDestination == address(0) || _destination.totalSupply() > topMigrationDestination.totalSupply()) {
            topMigrationDestination = _destination;
        }
        return true;
    }

    function migrateIn(address _reporter, uint256 _attotokens) public afterInitialized returns (bool) {
        IUniverse _parentUniverse = universe.getParentUniverse();
        require(ReputationToken(msg.sender) == _parentUniverse.getReputationToken());
        balances[_reporter] = balances[_reporter].add(_attotokens);
        // Only count tokens migrated toward the available to be matched in other universes. The bonus should not be added
        universe.increaseRepAvailableForExtraBondPayouts(_attotokens);
        if (_parentUniverse.getForkingMarket().getReportingState() != IMarket.ReportingState.FINALIZED) {
            mint(_reporter, _attotokens.div(Reporting.forkMigrationPercentageBonusDivisor()));
        }
        supply = supply.add(_attotokens);
        return true;
    }

    function migrateFromLegacyReputationToken() public afterInitialized returns (bool) {
        var _legacyRepToken = ERC20(controller.lookup("LegacyReputationToken"));
        uint256 _legacyBalance = _legacyRepToken.balanceOf(msg.sender);
        _legacyRepToken.transferFrom(msg.sender, address(0), _legacyBalance);
        balances[msg.sender] = balances[msg.sender].add(_legacyBalance);
        supply = supply.add(_legacyBalance);
        return true;
    }

    function mintForDisputeBondMigration(uint256 _amount) public afterInitialized returns (bool) {
        IUniverse _parentUniverse = universe.getParentUniverse();
        require(_parentUniverse.isContainerForDisputeBondToken(IDisputeBond(msg.sender)));
        mint(msg.sender, _amount);
    }

    // AUDIT: check for reentrancy issues here, _source and _destination will be called as contracts during validation
    function trustedReportingWindowTransfer(address _source, address _destination, uint256 _attotokens) public afterInitialized returns (bool) {
        require(universe.isContainerForReportingWindow(IReportingWindow(msg.sender)));
        return internalTrustedTransfer(_source, _destination, _attotokens);
    }

        // AUDIT: check for reentrancy issues here, _source and _destination will be called as contracts during validation
    function trustedMarketTransfer(address _source, address _destination, uint256 _attotokens) public afterInitialized returns (bool) {
        require(universe.isContainerForMarket(IMarket(msg.sender)));
        return internalTrustedTransfer(_source, _destination, _attotokens);
    }

        // AUDIT: check for reentrancy issues here, _source and _destination will be called as contracts during validation
    function trustedStakeTokenTransfer(address _source, address _destination, uint256 _attotokens) public afterInitialized returns (bool) {
        require(universe.isContainerForStakeToken(IStakeToken(msg.sender)));
        return internalTrustedTransfer(_source, _destination, _attotokens);
    }

    function internalTrustedTransfer(address _source, address _destination, uint256 _attotokens) internal afterInitialized returns (bool) {
        balances[_source] = balances[_source].sub(_attotokens);
        balances[_destination] = balances[_destination].add(_attotokens);
        supply = supply.add(_attotokens);
        Transfer(_source, _destination, _attotokens);
        return true;
    }

    function assertReputationTokenIsLegit(IReputationToken _shadyReputationToken) private view returns (bool) {
        var _shadyUniverse = _shadyReputationToken.getUniverse();
        require(universe.isParentOf(_shadyUniverse));
        var _legitUniverse = _shadyUniverse;
        require(_legitUniverse.getReputationToken() == _shadyReputationToken);
        return true;
    }

    function getTypeName() public view returns (bytes32) {
        return "ReputationToken";
    }

    function getUniverse() public view returns (IUniverse) {
        return universe;
    }

    function getTopMigrationDestination() public view returns (IReputationToken) {
        return topMigrationDestination;
    }
}
