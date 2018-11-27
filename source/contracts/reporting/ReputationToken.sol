pragma solidity 0.4.24;

import 'reporting/IV2ReputationToken.sol';
import 'Controlled.sol';
import 'libraries/ITyped.sol';
import 'libraries/token/VariableSupplyToken.sol';
import 'libraries/token/ERC20.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IMarket.sol';
import 'reporting/Reporting.sol';
import 'reporting/IDisputeCrowdsourcer.sol';
import 'libraries/math/SafeMathUint256.sol';


contract ReputationToken is Controlled, ITyped, VariableSupplyToken, IV2ReputationToken {
    using SafeMathUint256 for uint256;

    string constant public name = "Reputation";
    string constant public symbol = "REP";
    uint8 constant public decimals = 18;
    IUniverse internal universe;
    IUniverse internal parentUniverse;
    uint256 internal totalMigrated;
    uint256 internal totalTheoreticalSupply;

    constructor(IController _controller, IUniverse _universe, IUniverse _parentUniverse) public {
        require(_universe != address(0));
        controller = _controller;
        universe = _universe;
        parentUniverse = _parentUniverse;
        updateTotalTheoreticalSupply();
    }

    function migrateOutByPayout(uint256[] _payoutNumerators, uint256 _attotokens) public returns (bool) {
        require(_attotokens > 0);
        IUniverse _destinationUniverse = universe.createChildUniverse(_payoutNumerators);
        IReputationToken _destination = _destinationUniverse.getReputationToken();
        burn(msg.sender, _attotokens);
        _destination.migrateIn(msg.sender, _attotokens);
        return true;
    }

    function migrateOut(IReputationToken _destination, uint256 _attotokens) public returns (bool) {
        require(_attotokens > 0);
        assertReputationTokenIsLegitSibling(_destination);
        burn(msg.sender, _attotokens);
        _destination.migrateIn(msg.sender, _attotokens);
        return true;
    }

    function migrateIn(address _reporter, uint256 _attotokens) public returns (bool) {
        IUniverse _parentUniverse = universe.getParentUniverse();
        require(ReputationToken(msg.sender) == _parentUniverse.getReputationToken());
        require(controller.getTimestamp() < _parentUniverse.getForkEndTime());
        mint(_reporter, _attotokens);
        totalMigrated += _attotokens;
        // Update the fork tenative winner and finalize if we can
        if (!_parentUniverse.getForkingMarket().isFinalized()) {
            _parentUniverse.updateTentativeWinningChildUniverse(universe.getParentPayoutDistributionHash());
        }
        return true;
    }

    function mintForReportingParticipant(uint256 _amountMigrated) public returns (bool) {
        IUniverse _parentUniverse = universe.getParentUniverse();
        IReportingParticipant _reportingParticipant = IReportingParticipant(msg.sender);
        require(_parentUniverse.isContainerForReportingParticipant(_reportingParticipant));
        uint256 _bonus = _amountMigrated.mul(2) / 5;
        mint(_reportingParticipant, _bonus);
        return true;
    }

    function mintForAuction(uint256 _amountToMint) public returns (bool) {
        require(universe.getAuction() == IAuction(msg.sender));
        mint(msg.sender, _amountToMint);
        return true;
    }

    function burnForAuction(uint256 _amountToBurn) public returns (bool) {
        require(universe.getAuction() == IAuction(msg.sender));
        burn(msg.sender, _amountToBurn);
        return true;
    }

    function burnForMarket(uint256 _amountToBurn) public returns (bool) {
        require(universe.isContainerForMarket(IMarket(msg.sender)));
        burn(msg.sender, _amountToBurn);
        return true;
    }

    function transfer(address _to, uint _value) public returns (bool) {
        return super.transfer(_to, _value);
    }

    function transferFrom(address _from, address _to, uint _value) public returns (bool) {
        return super.transferFrom(_from, _to, _value);
    }

    function trustedUniverseTransfer(address _source, address _destination, uint256 _attotokens) public returns (bool) {
        require(IUniverse(msg.sender) == universe);
        return internalTransfer(_source, _destination, _attotokens);
    }

    function trustedMarketTransfer(address _source, address _destination, uint256 _attotokens) public returns (bool) {
        require(universe.isContainerForMarket(IMarket(msg.sender)));
        return internalTransfer(_source, _destination, _attotokens);
    }

    function trustedReportingParticipantTransfer(address _source, address _destination, uint256 _attotokens) public returns (bool) {
        require(universe.isContainerForReportingParticipant(IReportingParticipant(msg.sender)));
        return internalTransfer(_source, _destination, _attotokens);
    }

    function trustedDisputeWindowTransfer(address _source, address _destination, uint256 _attotokens) public returns (bool) {
        require(universe.isContainerForDisputeWindow(IDisputeWindow(msg.sender)));
        return internalTransfer(_source, _destination, _attotokens);
    }

    function trustedAuctionTransfer(address _source, address _destination, uint256 _attotokens) public returns (bool) {
        require(universe.getAuction() == (IAuction(msg.sender)));
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

    function updateTotalTheoreticalSupply() public returns (bool) {
        if (parentUniverse == IUniverse(0)) {
            totalTheoreticalSupply = Reporting.getInitialREPSupply();
        } else if (controller.getTimestamp() >= parentUniverse.getForkEndTime()) {
            totalTheoreticalSupply = totalSupply();
        } else {
            totalTheoreticalSupply = totalSupply() + parentUniverse.getReputationToken().totalSupply();
        }
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

    function migrateFromLegacyReputationToken() public returns (bool) {
        ERC20 _legacyRepToken = ERC20(controller.lookup("LegacyReputationToken"));
        uint256 _legacyBalance = _legacyRepToken.balanceOf(msg.sender);
        require(_legacyRepToken.transferFrom(msg.sender, address(0), _legacyBalance));
        mint(msg.sender, _legacyBalance);
        return true;
    }
}
