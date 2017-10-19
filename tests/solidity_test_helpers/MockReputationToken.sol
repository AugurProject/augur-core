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
    IReputationToken private migrateOutDestinationValue;
    address private migrateOutReporterValue;
    uint256 private migrateOutAttoTokens;
    bool private setMigrateFromLegacyReputationTokenValue;
    IUniverse private initializeUniverseValue;
    address private trustedTransferSourceValue; 
    address private trustedTransferDestinationValue; 
    uint256 private trustedTransferAttotokensValue;
    uint256 private setBalanceOfValue;
    address private transferToValue;
    uint256 private transferValueValue;
    uint256[] private transferAmounts;
    address[] private transferAddresses;
    uint256[] private balanceOfAmounts;
    address[] private balanceOfAddresses;
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
    
    function setBalanceOf(uint256 _balance) public {
        setBalanceOfValue = _balance;
    }
    
    function getTransferToValue() public returns(address) {
        return transferToValue;
    }
    
    function getTransferValueValue() public returns(uint256) {
        return transferValueValue;
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

    function resetTransferToValues() public {
        transferToValue = address(0);
        transferValueValue = 0;
        transferAmounts = [0];
        transferAddresses = [0];
    }
    
    function resetBalanceOfValues() public {
        setBalanceOfValue = 0;
        balanceOfAmounts = [0];
        balanceOfAddresses = [0];
    }

    function getTransferValueFor(address _to) public returns(uint256) {
       for (uint8 j = 0; j < transferAddresses.length; j++) {
            if (transferAddresses[j] == _to) {
                return transferAmounts[j];
            }
        }
        return 0;
    }
    
    function setBalanceOfValueFor(address _to, uint256 _value) public returns(uint256) {
        balanceOfAmounts.push(_value);
        balanceOfAddresses.push(_to);
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
    
    function migrateOut(IReputationToken _destination, address _reporter, uint256 _attotokens) public returns (bool) {
        migrateOutDestinationValue = _destination;
        migrateOutReporterValue = _reporter;
        migrateOutAttoTokens = _attotokens;
        return setMigrateOutValue;
    }
    
    function migrateIn(address _reporter, uint256 _attotokens) public returns (bool) {
        return setMigrateInValue;
    }
    
    function mintForDisputeBondMigration(uint256 _amount) public returns (bool) {
        return setMintForDisputeBondMigrationValue;
    }
    
    function trustedTransfer(address _source, address _destination, uint256 _attotokens) public returns (bool) {
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
    
    function balanceOf(address _owner) public view returns (uint256) {
       for (uint8 j = 0; j < balanceOfAddresses.length; j++) {
            if (balanceOfAddresses[j] == _owner) {
                return balanceOfAmounts[j];
            }
        }
        return setBalanceOfValue;
    }
    
    function transfer(address _to, uint256 _value) public returns (bool) {
        transferToValue = _to;
        transferValueValue = _value;
        transferAmounts.push(_value);
        transferAddresses.push(_to);
        return true;
    }
}