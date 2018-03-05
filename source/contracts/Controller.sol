pragma solidity 0.4.20;

/**
 * The Controller is used to manage whitelisting of contracts and and halt the normal use of Augur’s contracts (e.g., if there is a vulnerability found in Augur).  There is only one instance of the Controller, and it gets uploaded to the blockchain before all of the other contracts.  The `owner` attribute of the Controller is set to the address that called the constructor of the Controller.  The Augur team can then call functions from this address to interact with the Controller.
 *
 * Initially, Augur will have a “dev mode” that that can be enabled to allow Augur’s team to suicide funds, extract Ether or Tokens from a specific contract (in case funds inadvertently get sent somewhere they shouldn’t have), and update the Controller of a target contract to a new Controller.  Eventually, the plan is to remove this mode so that this functionality will no longer be available to anyone, including the Augur team.  At that point, the `owner` address will only be able to the `emergencyStop` and `release` functions.
 */

import 'IAugur.sol';
import 'IController.sol';
import 'IControlled.sol';
import 'libraries/token/ERC20Basic.sol';
import 'ITime.sol';


contract Controller is IController {
    struct ContractDetails {
        bytes32 name;
        address contractAddress;
        bytes20 commitHash;
        bytes32 bytecodeHash;
    }

    address public owner;
    mapping(address => bool) public whitelist;
    mapping(bytes32 => ContractDetails) public registry;

    modifier onlyWhitelistedCallers {
        assertIsWhitelisted(msg.sender);
        _;
    }

    modifier devModeOwnerOnly {
        require(msg.sender == owner);
        require(whitelist[owner]);
        _;
    }

    modifier onlyOwnerCaller {
        require(msg.sender == owner);
        _;
    }

    modifier onlyInBadTimes {
        require(isStopped());
        _;
    }

    modifier onlyInGoodTimes {
        require(!isStopped());
        _;
    }

    function Controller() public {
        owner = msg.sender;
        whitelist[owner] = true;
    }

    /*
     * Whitelisting [whitelisted augur contracts and dev mode can use it]
     */

    function addToWhitelist(address _target) public onlyWhitelistedCallers returns (bool) {
        whitelist[_target] = true;
        getAugur().logContractAddedToWhitelist(_target);
        return true;
    }

    function removeFromWhitelist(address _target) public onlyWhitelistedCallers returns (bool) {
        whitelist[_target] = false;
        return true;
    }

    function assertIsWhitelisted(address _target) public view returns (bool) {
        require(whitelist[_target]);
        return true;
    }

    /*
     * Contract Administration [dev mode can use it]
     */

    function registerContract(bytes32 _key, address _address, bytes20 _commitHash, bytes32 _bytecodeHash) public devModeOwnerOnly returns (bool) {
        registry[_key] = ContractDetails(_key, _address, _commitHash, _bytecodeHash);
        getAugur().logContractAddedToRegistry(_key, _address, _commitHash, _bytecodeHash);
        return true;
    }

    function getContractDetails(bytes32 _key) public view returns (address, bytes20, bytes32) {
        ContractDetails storage _details = registry[_key];
        return (_details.contractAddress, _details.commitHash, _details.bytecodeHash);
    }

    function unregisterContract(bytes32 _key) public devModeOwnerOnly returns (bool) {
        delete registry[_key];
        return true;
    }

    function lookup(bytes32 _key) public view returns (address) {
        return registry[_key].contractAddress;
    }

    function suicideFunds(IControlled _target, address _destination, ERC20Basic[] _tokens) public devModeOwnerOnly returns (bool) {
        _target.suicideFunds(_destination, _tokens);
        return true;
    }

    function updateController(IControlled _target, Controller _newController) public devModeOwnerOnly returns (bool) {
        _target.setController(_newController);
        return true;
    }

     /*
     * Controller Administration [dev can transfer ownership anytime, mode can only switched from dev mode -> decentralized]
     */

    function transferOwnership(address _newOwner) public onlyOwnerCaller returns (bool) {
        // if in dev mode, blacklist old owner and whitelist new owner
        if (whitelist[owner]) {
            whitelist[owner] = false;
            whitelist[_newOwner] = true;
        }
        owner = _newOwner;
        return true;
    }

    function switchOffDevMode() public devModeOwnerOnly returns (bool) {
        whitelist[owner] = false;
        return true;
    }

    function stopInEmergency() public view onlyInGoodTimes returns (bool) {
        return true;
    }

    function onlyInEmergency() public view onlyInBadTimes returns (bool) {
        return true;
    }

    function isStopped() public view returns (bool) {
        return registry["EmergencyStop"].contractAddress != address(0);
    }

    /*
     * Helper functions
     */

    function getAugur() public view returns (IAugur) {
        return IAugur(lookup("Augur"));
    }

    function getTimestamp() public view returns (uint256) {
        return ITime(lookup("Time")).getTimestamp();
    }
}
