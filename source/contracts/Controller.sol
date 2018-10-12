pragma solidity 0.4.24;

/**
 * The Controller is used to manage whitelisting of contracts and and halt the normal use of Augur’s contracts (e.g., if there is a vulnerability found in Augur).  There is only one instance of the Controller, and it gets uploaded to the blockchain before all of the other contracts.  The `owner` attribute of the Controller is set to the address that called the constructor of the Controller.  The Augur team can then call functions from this address to interact with the Controller.
 *
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
    }

    mapping(address => bool) public whitelist;
    mapping(bytes32 => ContractDetails) public registry;
    // In deployment mode the registration and whitelisting of contracts is permitted. Once turned off it can not be turned back on and no new contracts may be registered or whitelisted.
    bool public deploymentMode = true;

    modifier onlyInDeploymentMode {
        require(deploymentMode);
        _;
    }

    modifier onlyOwnerCaller {
        require(msg.sender == owner);
        _;
    }

    constructor() public {
        owner = msg.sender;
        whitelist[msg.sender] = true;
    }

    /*
     * Contract Administration
     */

    function addToWhitelist(address _target) public onlyInDeploymentMode onlyOwnerCaller returns (bool) {
        whitelist[_target] = true;
        return true;
    }

    function removeFromWhitelist(address _target) public onlyInDeploymentMode onlyOwnerCaller returns (bool) {
        whitelist[_target] = false;
        return true;
    }

    function assertIsWhitelisted(address _target) public view returns (bool) {
        require(whitelist[_target]);
        return true;
    }

    function registerContract(bytes32 _key, address _address) public onlyInDeploymentMode onlyOwnerCaller returns (bool) {
        require(registry[_key].contractAddress == address(0));
        registry[_key] = ContractDetails(_key, _address);
        return true;
    }

    function lookup(bytes32 _key) public view returns (address) {
        return registry[_key].contractAddress;
    }

    function transferOwnership(address _newOwner) public onlyOwnerCaller returns (bool) {
        owner = _newOwner;
        return true;
    }

    function turnOffDeploymentMode() public onlyInDeploymentMode onlyOwnerCaller returns (bool) {
        deploymentMode = false;
        return true;
    }

    // Price Feed Functions

    function toggleFeedSource(bool _useAuction) public onlyOwnerCaller returns (bool) {
        useAuction = _useAuction;
        return true;
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
