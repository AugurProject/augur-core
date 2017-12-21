pragma solidity 0.4.18;


import 'reporting/IReputationToken.sol';
import 'libraries/DelegationTarget.sol';
import 'libraries/ITyped.sol';
import 'libraries/Initializable.sol';
import 'libraries/token/VariableSupplyToken.sol';
import 'libraries/token/ERC20.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IMarket.sol';
import 'reporting/Reporting.sol';
import 'reporting/IDisputeCrowdsourcer.sol';
import 'libraries/math/SafeMathUint256.sol';
import 'libraries/Extractable.sol';


contract ReputationToken is DelegationTarget, Extractable, ITyped, Initializable, VariableSupplyToken, IReputationToken {
    using SafeMathUint256 for uint256;

    string constant public name = "Reputation";
    string constant public symbol = "REP";
    uint256 constant public decimals = 18;
    IUniverse private universe;

    function initialize(IUniverse _universe) public onlyInGoodTimes beforeInitialized returns (bool) {
        endInitialization();
        require(_universe != address(0));
        universe = _universe;
        return true;
    }

    function migrateOut(IReputationToken _destination, uint256 _attotokens) public onlyInGoodTimes afterInitialized returns (bool) {
        require(_attotokens > 0);
        assertReputationTokenIsLegit(_destination);
        burn(msg.sender, _attotokens);
        _destination.migrateIn(msg.sender, _attotokens);
        return true;
    }

    function migrateIn(address _reporter, uint256 _attotokens) public onlyInGoodTimes afterInitialized returns (bool) {
        IUniverse _parentUniverse = universe.getParentUniverse();
        require(ReputationToken(msg.sender) == _parentUniverse.getReputationToken());
        mint(_reporter, _attotokens);
        // Award a bonus if migration is done before the fork has resolved and check if the fork can be resolved early
        if (!_parentUniverse.getForkingMarket().isFinalized()) {
            mint(_reporter, _attotokens.div(Reporting.getForkMigrationPercentageBonusDivisor()));
            if (supply > _parentUniverse.getForkReputationGoal()) {
                _parentUniverse.getForkingMarket().finalizeFork();
            }
        }
        return true;
    }

    function migrateFromLegacyReputationToken() public onlyInGoodTimes afterInitialized returns (bool) {
        ERC20 _legacyRepToken = ERC20(controller.lookup("LegacyReputationToken"));
        uint256 _legacyBalance = _legacyRepToken.balanceOf(msg.sender);
        _legacyRepToken.transferFrom(msg.sender, address(0), _legacyBalance);
        mint(msg.sender, _legacyBalance);
        return true;
    }

    function mintForReportingParticipant(uint256 _amountMigrated) public onlyInGoodTimes afterInitialized returns (bool) {
        IUniverse _parentUniverse = universe.getParentUniverse();
        IReportingParticipant _reportingParticipant = IReportingParticipant(msg.sender);
        require(_parentUniverse.isContainerForReportingParticipant(_reportingParticipant));
        mint(_reportingParticipant, _amountMigrated / 2);
        return true;
    }

    // AUDIT: check for reentrancy issues here, _source and _destination will be called as contracts during validation
    function trustedUniverseTransfer(address _source, address _destination, uint256 _attotokens) public onlyInGoodTimes afterInitialized returns (bool) {
        require(IUniverse(msg.sender) == universe);
        return internalTransfer(_source, _destination, _attotokens);
    }

    // AUDIT: check for reentrancy issues here, _source and _destination will be called as contracts during validation
    function trustedMarketTransfer(address _source, address _destination, uint256 _attotokens) public onlyInGoodTimes afterInitialized returns (bool) {
        require(universe.isContainerForMarket(IMarket(msg.sender)));
        return internalTransfer(_source, _destination, _attotokens);
    }

    // AUDIT: check for reentrancy issues here, _source and _destination will be called as contracts during validation
    function trustedReportingParticipantTransfer(address _source, address _destination, uint256 _attotokens) public onlyInGoodTimes afterInitialized returns (bool) {
        require(universe.isContainerForReportingParticipant(IReportingParticipant(msg.sender)));
        return internalTransfer(_source, _destination, _attotokens);
    }

    // AUDIT: check for reentrancy issues here, _source and _destination will be called as contracts during validation
    function trustedFeeWindowTransfer(address _source, address _destination, uint256 _attotokens) public onlyInGoodTimes afterInitialized returns (bool) {
        require(universe.isContainerForFeeWindow(IFeeWindow(msg.sender)));
        return internalTransfer(_source, _destination, _attotokens);
    }

    function assertReputationTokenIsLegit(IReputationToken _shadyReputationToken) private view returns (bool) {
        IUniverse _shadyUniverse = _shadyReputationToken.getUniverse();
        require(universe.isParentOf(_shadyUniverse));
        IUniverse _legitUniverse = _shadyUniverse;
        require(_legitUniverse.getReputationToken() == _shadyReputationToken);
        return true;
    }

    function getTypeName() public view returns (bytes32) {
        return "ReputationToken";
    }

    function getUniverse() public view returns (IUniverse) {
        return universe;
    }

    function onTokenTransfer(address _from, address _to, uint256 _value) internal returns (bool) {
        controller.getAugur().logReputationTokensTransferred(universe, _from, _to, _value);
        return true;
    }

    function onMint(address _target, uint256 _amount) internal returns (bool) {
        controller.getAugur().logReputationTokenMinted(universe, _target, _amount);
        return true;
    }

    function onBurn(address _target, uint256 _amount) internal returns (bool) {
        controller.getAugur().logReputationTokenBurned(universe, _target, _amount);
        return true;
    }

    function getProtectedTokens() internal returns (address[] memory) {
        return new address[](0);
    }
}
