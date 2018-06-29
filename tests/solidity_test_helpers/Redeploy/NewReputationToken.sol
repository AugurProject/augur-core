pragma solidity 0.4.20;

import 'reporting/IReputationToken.sol';
import 'libraries/DelegationTarget.sol';
import 'libraries/ITyped.sol';
import 'libraries/Initializable.sol';
import 'libraries/token/VariableSupplyToken.sol';
import 'libraries/token/ERC20.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IMarket.sol';
import 'reporting/Reporting.sol';
import 'reporting/ReputationToken.sol';
import 'reporting/IDisputeCrowdsourcer.sol';
import 'libraries/math/SafeMathUint256.sol';


contract NewReputationToken is DelegationTarget, ITyped, Initializable, VariableSupplyToken, IReputationToken {
    using SafeMathUint256 for uint256;

    string constant public name = "Reputation";
    string constant public symbol = "REP";
    uint8 constant public decimals = 18;
    IUniverse private universe;
    uint256 private totalMigrated;
    mapping(address => uint256) migratedToSibling;
    uint256 private parentTotalTheoreticalSupply;
    uint256 private totalTheoreticalSupply;

    function initialize(IUniverse _universe) public onlyInGoodTimes beforeInitialized returns (bool) {
        endInitialization();
        require(_universe != address(0));
        universe = _universe;
        updateParentTotalTheoreticalSupply();
        return true;
    }

    function migrateOutByPayout(uint256[] _payoutNumerators, bool _invalid, uint256 _attotokens) public onlyInGoodTimes afterInitialized returns (bool) {
        require(_attotokens > 0);
        IUniverse _destinationUniverse = universe.createChildUniverse(_payoutNumerators, _invalid);
        IReputationToken _destination = _destinationUniverse.getReputationToken();
        burn(msg.sender, _attotokens);
        _destination.migrateIn(msg.sender, _attotokens);
        return true;
    }

    function migrateOut(IReputationToken _destination, uint256 _attotokens) public onlyInGoodTimes afterInitialized returns (bool) {
        require(_attotokens > 0);
        assertReputationTokenIsLegitSibling(_destination);
        burn(msg.sender, _attotokens);
        _destination.migrateIn(msg.sender, _attotokens);
        return true;
    }

    function migrateIn(address _reporter, uint256 _attotokens) public onlyInGoodTimes afterInitialized returns (bool) {
        IUniverse _parentUniverse = universe.getParentUniverse();
        require(ReputationToken(msg.sender) == _parentUniverse.getReputationToken());
        mint(_reporter, _attotokens);
        totalMigrated += _attotokens;
        // Award a bonus if migration is done before the fork period is over, even if it has finalized
        if (controller.getTimestamp() < _parentUniverse.getForkEndTime()) {
            uint256 _bonus = _attotokens.div(Reporting.getForkMigrationPercentageBonusDivisor());
            mint(_reporter, _bonus);
            totalTheoreticalSupply += _bonus;
        }
        // Update the fork tenative winner and finalize if we can
        if (!_parentUniverse.getForkingMarket().isFinalized()) {
            _parentUniverse.updateTentativeWinningChildUniverse(universe.getParentPayoutDistributionHash());
        }
        return true;
    }

    function mintForReportingParticipant(uint256 _amountMigrated) public onlyInGoodTimes afterInitialized returns (bool) {
        IUniverse _parentUniverse = universe.getParentUniverse();
        IReportingParticipant _reportingParticipant = IReportingParticipant(msg.sender);
        require(_parentUniverse.isContainerForReportingParticipant(_reportingParticipant));
        uint256 _bonus = _amountMigrated.div(2);
        mint(_reportingParticipant, _bonus);
        totalTheoreticalSupply += _bonus;
        return true;
    }

    function transfer(address _to, uint _value) public returns (bool) {
        return super.transfer(_to, _value);
    }

    function transferFrom(address _from, address _to, uint _value) public returns (bool) {
        return super.transferFrom(_from, _to, _value);
    }

    function trustedUniverseTransfer(address _source, address _destination, uint256 _attotokens) public onlyInGoodTimes afterInitialized returns (bool) {
        require(IUniverse(msg.sender) == universe);
        return internalTransfer(_source, _destination, _attotokens);
    }

    function trustedMarketTransfer(address _source, address _destination, uint256 _attotokens) public onlyInGoodTimes afterInitialized returns (bool) {
        require(universe.isContainerForMarket(IMarket(msg.sender)));
        return internalTransfer(_source, _destination, _attotokens);
    }

    function trustedReportingParticipantTransfer(address _source, address _destination, uint256 _attotokens) public onlyInGoodTimes afterInitialized returns (bool) {
        require(universe.isContainerForReportingParticipant(IReportingParticipant(msg.sender)));
        return internalTransfer(_source, _destination, _attotokens);
    }

    function trustedFeeWindowTransfer(address _source, address _destination, uint256 _attotokens) public onlyInGoodTimes afterInitialized returns (bool) {
        require(universe.isContainerForFeeWindow(IFeeWindow(msg.sender)));
        return internalTransfer(_source, _destination, _attotokens);
    }

    function assertReputationTokenIsLegitSibling(IReputationToken _shadyReputationToken) private view returns (bool) {
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

    function getTotalMigrated() public view returns (uint256) {
        return totalMigrated;
    }

    function getLegacyRepToken() public view returns (ERC20) {
        return ERC20(controller.lookup("LegacyReputationToken"));
    }

    function updateSiblingMigrationTotal(IReputationToken _token) public returns (bool) {
        require(_token != this);
        IUniverse _shadyUniverse = _token.getUniverse();
        require(_token == universe.getParentUniverse().getChildUniverse(_shadyUniverse.getParentPayoutDistributionHash()).getReputationToken());
        totalTheoreticalSupply += migratedToSibling[_token];
        migratedToSibling[_token] = _token.getTotalMigrated();
        totalTheoreticalSupply -= migratedToSibling[_token];
        return true;
    }

    function updateParentTotalTheoreticalSupply() public returns (bool) {
        IUniverse _parentUniverse = universe.getParentUniverse();
        totalTheoreticalSupply -= parentTotalTheoreticalSupply;
        if (_parentUniverse == IUniverse(0)) {
            parentTotalTheoreticalSupply = Reporting.getInitialREPSupply();
        } else {
            parentTotalTheoreticalSupply = _parentUniverse.getReputationToken().getTotalTheoreticalSupply();
        }
        totalTheoreticalSupply += parentTotalTheoreticalSupply;
        return true;
    }

    function getTotalTheoreticalSupply() public view returns (uint256) {
        return totalTheoreticalSupply;
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

    function migrateFromLegacyReputationToken() public onlyInGoodTimes afterInitialized returns (bool) {
        ERC20 _legacyRepToken = ERC20(controller.lookup("LegacyReputationToken"));
        uint256 _legacyBalance = _legacyRepToken.balanceOf(msg.sender);
        require(_legacyRepToken.transferFrom(msg.sender, address(0), _legacyBalance));
        mint(msg.sender, _legacyBalance);
        return true;
    }
}
