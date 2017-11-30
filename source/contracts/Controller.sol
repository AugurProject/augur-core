pragma solidity 0.4.18;

/**
 * The Controller is used to manage whitelisting of contracts and and halt the normal use of Augur’s contracts (e.g., if there is a vulnerability found in Augur).  There is only one instance of the Controller, and it gets uploaded to the blockchain before all of the other contracts.  The `owner` attribute of the Controller is set to the address that called the constructor of the Controller.  The Augur team can then call functions from this address to interact with the Controller.
 *
 * If Augur needs to be halted for some reason (such as a bug being found that needs to be fixed before trading can continue), the `owner` address can call the `emergencyStop` function (and later the `release` function) to make the system stop/resume.  When in the stopped state, users can only call the `withdrawInEmergency` function on dispute bonds, markets, participation tokens, and stake tokens to withdraw any funds they have in Augur as REP.  All other functionality in Augur is disabled when it is in the stopped state.  (Additionally, the `withdrawInEmergency` function cannot be called when Augur is not in the stopped state.)  The modifier `onlyInGoodTimes` is used for functions that should only be useable when Augur is not stopped, and the modifier `onlyInBadTimes` is used for functions that should only be useable when Augur is stopped.
 *
 * Initially, Augur will have a “dev mode” that that can be enabled to allow Augur’s team to suicide funds, extract Ether or Tokens from a specific contract (in case funds inadvertently get sent somewhere they shouldn’t have), and update the Controller of a target contract to a new Controller.  Eventually, the plan is to remove this mode so that this functionality will no longer be available to anyone, including the Augur team.  At that point, the `owner` address will only be able to the `emergencyStop` and `release` functions.
 */

import 'IController.sol';
import 'IControlled.sol';
import 'libraries/token/ERC20Basic.sol';
import 'libraries/Extractable.sol';
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
    // TODO: remove the registry in favor of registeredContracts
    mapping(bytes32 => ContractDetails) public registry;
    bool public stopped = false;

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
        require(stopped);
        _;
    }

    modifier onlyInGoodTimes {
        require(!stopped);
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
     * Registry for lookups [whitelisted augur contracts and dev mode can use it]
     */

    function registerContract(bytes32 _key, address _address, bytes20 _commitHash, bytes32 _bytecodeHash) public onlyOwnerCaller returns (bool) {
        registry[_key] = ContractDetails(_key, _address, _commitHash, _bytecodeHash);
        return true;
    }

    function getContractDetails(bytes32 _key) public view returns (address, bytes20, bytes32) {
        ContractDetails storage _details = registry[_key];
        return (_details.contractAddress, _details.commitHash, _details.bytecodeHash);
    }

    function unregisterContract(bytes32 _key) public onlyOwnerCaller returns (bool) {
        delete registry[_key];
        return true;
    }

    function lookup(bytes32 _key) public view returns (address) {
        return registry[_key].contractAddress;
    }

    function assertOnlySpecifiedCaller(address _caller, bytes32 _allowedCaller) public view returns (bool) {
        require(registry[_allowedCaller].contractAddress == _caller || (msg.sender == owner && whitelist[owner]));
        return true;
    }

    /*
     * Contract Administration [dev mode can use it]
     */

    function suicideFunds(IControlled _target, address _destination, ERC20Basic[] _tokens) public devModeOwnerOnly returns (bool) {
        _target.suicideFunds(_destination, _tokens);
        return true;
    }

    function extractEther(Extractable _target, address _destination) public devModeOwnerOnly returns (bool) {
        _target.extractEther(_destination);
        return true;
    }

    function extractTokens(Extractable _target, address _destination, ERC20Basic _token) public devModeOwnerOnly returns (bool) {
        _target.extractTokens(_destination, _token);
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

    function switchModeSoOnlyEmergencyStopsAndEscapeHatchesCanBeUsed() public devModeOwnerOnly returns (bool) {
        whitelist[owner] = false;
        return true;
    }

    /*
     * Emergency Stop Functions [dev can use it anytime in or out of dev mode]
     */

    function emergencyStop() public onlyOwnerCaller onlyInGoodTimes returns (bool) {
        stopped = true;
        return true;
    }

    function release() public onlyOwnerCaller onlyInBadTimes returns (bool) {
        stopped = false;
        return true;
    }

    function stopInEmergency() public view onlyInGoodTimes returns (bool) {
        return true;
    }

    function onlyInEmergency() public view onlyInBadTimes returns (bool) {
        return true;
    }

    /*
     * Helper functions
     */

    function getAugur() public view returns (Augur) {
        return Augur(lookup("Augur"));
    }

    function getTimestamp() public view returns (uint256) {
        return ITime(lookup("Time")).getTimestamp();
    }
}
