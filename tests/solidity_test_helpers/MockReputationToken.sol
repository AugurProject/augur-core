pragma solidity ^0.4.17;

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

contract MockReputationToken is DelegationTarget, ITyped, Initializable, VariableSupplyToken, IReputationToken {
    using SafeMathUint256 for uint256;

    bool private setMigrateOutValue;
    bool private setMigrateInValue;
    bool private setMintForDisputeBondMigrationValue;
    bool private setTrustedTransferValue;
    IUniverse private setUniverseValue;
    IReputationToken private setTopMigrationDestinationValue;
    bool private setMigrateFromLegacyRepContractValue;
    
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
    function setMigrateFromLegacyRepContract(bool _setMigrateFromLegacyRepContractValue) public {
        setMigrateFromLegacyRepContractValue = _setMigrateFromLegacyRepContractValue;
    }
    /*
    * Impl of IReputationToken and ITyped
     */
    function getTypeName() public view returns (bytes32) {
        return "ReputationToken";
    }     
    function initialize(IUniverse _universe) public returns (bool) {
        endInitialization();
        setUniverseValue = _universe;
        return true;
    }
    function migrateOut(IReputationToken _destination, address _reporter, uint256 _attotokens) public returns (bool) {
        return setMigrateOutValue;
    }
    function migrateIn(address _reporter, uint256 _attotokens) public returns (bool) {
        return setMigrateInValue;
    }
    function mintForDisputeBondMigration(uint256 _amount) public returns (bool) {
        return setMintForDisputeBondMigrationValue;
    }
    function trustedTransfer(address _source, address _destination, uint256 _attotokens) public returns (bool) {
        return setTrustedTransferValue;
    }
    function getUniverse() public view returns (IUniverse) {
        return setUniverseValue;
    }
    function getTopMigrationDestination() public view returns (IReputationToken) {
        return setTopMigrationDestinationValue;
    }
    function migrateFromLegacyRepContract() public afterInitialized returns (bool) {
        return setMigrateFromLegacyRepContractValue;
    }
}