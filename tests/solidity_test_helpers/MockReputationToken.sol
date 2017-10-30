pragma solidity ^0.4.17;

import 'reporting/IReputationToken.sol';
import 'libraries/DelegationTarget.sol';
import 'libraries/ITyped.sol';
import 'libraries/Initializable.sol';
import 'libraries/token/ERC20.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IMarket.sol';
import 'reporting/Reporting.sol';
import 'libraries/math/SafeMathUint256.sol';
import 'TEST/MockVariableSupplyToken.sol';


contract MockReputationToken is DelegationTarget, ITyped, Initializable, MockVariableSupplyToken, IReputationToken {
    using SafeMathUint256 for uint256;

    bool private setMigrateOutValue;
    bool private setMigrateInValue;
    bool private setMintForDisputeBondMigrationValue;
    bool private setTrustedTransferValue;
    IUniverse private setUniverseValue;
    IReputationToken private setTopMigrationDestinationValue;
    IReputationToken private migrateOutDestinationValue;
    address private migrateOutReporterValue;
    uint256 private migrateOutAttoTokens;
    bool private setMigrateFromLegacyReputationTokenValue;
    IUniverse private initializeUniverseValue;
    address private trustedTransferSourceValue;
    address private trustedTransferDestinationValue;
    uint256 private trustedTransferAttotokensValue;
    address private migrateInReporterValue;
    uint256 private migrateInAttoTokensValue;
    bool private migrateInBonusIfInForkWindowValue;

    /*
    * setters to feed the getters and impl of IUniverse
    */
    function setMigrateOut(bool _setMigrateOutValue) public {
        setMigrateOutValue = _setMigrateOutValue;
    }

    function setMigrateIn(bool _setMigrateInValue) public {
        setMigrateInValue = _setMigrateInValue;
    }

    function setMintForDisputeBondMigration(bool _setMintForDisputeBondMigrationValue) public {
        setMintForDisputeBondMigrationValue = _setMintForDisputeBondMigrationValue;
    }

    function setTrustedTransfer(bool _setTrustedTransferValue) public {
        setTrustedTransferValue = _setTrustedTransferValue;
    }

    function setUniverse(IUniverse _setUniverseValue) public {
        setUniverseValue = _setUniverseValue;
    }

    function setTopMigrationDestination(IReputationToken _setTopMigrationDestinationValue) public {
        setTopMigrationDestinationValue = _setTopMigrationDestinationValue;
    }

    function setMigrateFromLegacyReputationToken(bool _setMigrateFromLegacyReputationTokenValue) public {
        setMigrateFromLegacyReputationTokenValue = _setMigrateFromLegacyReputationTokenValue;
    }

    function setInitializeUniverseValue() public returns(IUniverse) {
        return initializeUniverseValue;
    }

    function getTrustedTransferSourceValue() public returns(address) {
        return trustedTransferSourceValue;
    }

    function getTrustedTransferDestinationValue() public returns(address) {
        return trustedTransferDestinationValue;
    }

    function getTrustedTransferAttotokensValue() public returns(uint256) {
        return trustedTransferAttotokensValue;
    }

    function getMigrateOutDestinationValue() public view returns(IReputationToken) {
        return migrateOutDestinationValue;
    }

    function getMigrateOutReporterValue() public returns(address) {
        return migrateOutReporterValue;
    }

    function getMigrateOutAttoTokens() public returns(uint256) {
        return migrateOutAttoTokens;
    }
    
    function getMigrateInReporterValue() public returns(address) {
        return migrateInReporterValue;
    }

    function getMigrateInAttoTokensValue() public returns(uint256) {
        return migrateInAttoTokensValue;
    }

    function getMigrateInBonusIfInForkWindowValue() public returns(bool) {
        return migrateInBonusIfInForkWindowValue;
    }

    function callIncreaseRepAvailableForExtraBondPayouts(IUniverse _universe, uint256 _amount) public returns(bool) {
        return _universe.increaseRepAvailableForExtraBondPayouts(_amount);
    }

    function callMigrateIn(IReputationToken _reputationToken, address _reporter, uint256 _attotokens, bool _bonusIfInForkWindow) public returns (bool) {
        return _reputationToken.migrateIn(_reporter, _attotokens, _bonusIfInForkWindow);
    }
    
    /*
    * Impl of IReputationToken and ITyped
     */
    function getTypeName() public view returns (bytes32) {
        return "ReputationToken";
    }

    function initialize(IUniverse _universe) public returns (bool) {
        endInitialization();
        initializeUniverseValue = _universe;
        return true;
    }

    function migrateOutStakeToken(IReputationToken _destination, address _reporter, uint256 _attotokens) public returns (bool) {
        migrateOutDestinationValue = _destination;
        migrateOutReporterValue = _reporter;
        migrateOutAttoTokens = _attotokens;
        return setMigrateOutValue;
    }

    function migrateOutDisputeBond(IReputationToken _destination, address _reporter, uint256 _attotokens) public returns (bool) {
        migrateOutDestinationValue = _destination;
        migrateOutReporterValue = _reporter;
        migrateOutAttoTokens = _attotokens;
        return setMigrateOutValue;
    }

    function migrateOut(IReputationToken _destination, address _reporter, uint256 _attotokens) public returns (bool) {
        migrateOutDestinationValue = _destination;
        migrateOutReporterValue = _reporter;
        migrateOutAttoTokens = _attotokens;
        return setMigrateOutValue;
    }

    function migrateIn(address _reporter, uint256 _attotokens, bool _bonusIfInForkWindow) public returns (bool) {
        migrateInReporterValue = _reporter;
        migrateInAttoTokensValue = _attotokens;
        migrateInBonusIfInForkWindowValue = _bonusIfInForkWindow;
        return setMigrateInValue;
    }

    function mintForDisputeBondMigration(uint256 _amount) public returns (bool) {
        return setMintForDisputeBondMigrationValue;
    }

    function trustedReportingWindowTransfer(address _source, address _destination, uint256 _attotokens) public returns (bool) {
        trustedTransferSourceValue = _source;
        trustedTransferDestinationValue = _destination;
        trustedTransferAttotokensValue = _attotokens;
        return setTrustedTransferValue;
    }

    function trustedMarketTransfer(address _source, address _destination, uint256 _attotokens) public returns (bool) {
        trustedTransferSourceValue = _source;
        trustedTransferDestinationValue = _destination;
        trustedTransferAttotokensValue = _attotokens;
        return setTrustedTransferValue;
    }

    function trustedStakeTokenTransfer(address _source, address _destination, uint256 _attotokens) public returns (bool) {
        trustedTransferSourceValue = _source;
        trustedTransferDestinationValue = _destination;
        trustedTransferAttotokensValue = _attotokens;
        return setTrustedTransferValue;
    }

    function trustedParticipationTokenTransfer(address _source, address _destination, uint256 _attotokens) public returns (bool) {
        trustedTransferSourceValue = _source;
        trustedTransferDestinationValue = _destination;
        trustedTransferAttotokensValue = _attotokens;
        return setTrustedTransferValue;
    }

    function getUniverse() public view returns (IUniverse) {
        return setUniverseValue;
    }

    function getTopMigrationDestination() public view returns (IReputationToken) {
        return setTopMigrationDestinationValue;
    }

    function migrateFromLegacyReputationToken() public afterInitialized returns (bool) {
        return setMigrateFromLegacyReputationTokenValue;
    }
}
