pragma solidity 0.4.17;


import 'IController.sol';
import 'IControlled.sol';
import 'libraries/token/ERC20Basic.sol';
import 'libraries/Extractable.sol';


contract Controller is IController {
    struct ContractDetails {
        bytes32 name;
        address contractAddress;
        bytes20 commitHash;
        bytes32 fileHash;
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

    function addToWhitelist(address _target) public onlyWhitelistedCallers returns(bool) {
        whitelist[_target] = true;
        return true;
    }

    function removeFromWhitelist(address _target) public onlyWhitelistedCallers returns(bool) {
        whitelist[_target] = false;
        return true;
    }

    function assertIsWhitelisted(address _target) public view returns(bool) {
        require(whitelist[_target]);
        return true;
    }

    /*
     * Registry for lookups [whitelisted augur contracts and dev mode can use it]
     */

    function registerContract(bytes32 _key, address _address, bytes20 _commitHash, bytes32 _fileHash) public onlyOwnerCaller returns(bool) {
        registry[_key] = ContractDetails(_key, _address, _commitHash, _fileHash);
        return true;
    }

    function getContractDetails(bytes32 _key) public view returns (address, bytes20, bytes32) {
        ContractDetails storage _details = registry[_key];
        return (_details.contractAddress, _details.commitHash, _details.fileHash);
    }

    function unregisterContract(bytes32 _key) public onlyOwnerCaller returns(bool) {
        delete registry[_key];
        return true;
    }

    function lookup(bytes32 _key) public view returns(address) {
        return registry[_key].contractAddress;
    }

    function assertOnlySpecifiedCaller(address _caller, bytes32 _allowedCaller) public view returns(bool) {
        require(registry[_allowedCaller].contractAddress == _caller || (msg.sender == owner && whitelist[owner]));
        return true;
    }

    /*
     * Contract Administration [dev mode can use it]
     */

    function suicideFunds(IControlled _target, address _destination, ERC20Basic[] _tokens) public devModeOwnerOnly returns(bool) {
        _target.suicideFunds(_destination, _tokens);
        return true;
    }

    function extractEther(Extractable _target, address _destination) public devModeOwnerOnly returns(bool) {
        _target.extractEther(_destination);
        return true;
    }

    function extractTokens(Extractable _target, address _destination, ERC20Basic _token) public devModeOwnerOnly returns(bool) {
        _target.extractTokens(_destination, _token);
        return true;
    }

    function updateController(IControlled _target, Controller _newController) public devModeOwnerOnly returns(bool) {
        _target.setController(_newController);
        return true;
    }

     /*
     * Controller Administration [dev can transfer ownership anytime, mode can only switched from dev mode -> decentralized]
     */

    function transferOwnership(address _newOwner) public onlyOwnerCaller returns(bool) {
        // if in dev mode, blacklist old owner and whitelist new owner
        if (whitelist[owner]) {
            whitelist[owner] = false;
            whitelist[_newOwner] = true;
        }
        owner = _newOwner;
        return true;
    }

    function switchModeSoOnlyEmergencyStopsAndEscapeHatchesCanBeUsed() public devModeOwnerOnly returns(bool) {
        whitelist[owner] = false;
        return true;
    }

    /*
     * Emergency Stop Functions [dev can use it anytime in or out of dev mode]
     */

    function emergencyStop() public onlyOwnerCaller onlyInGoodTimes returns(bool) {
        stopped = true;
        return true;
    }

    function release() public onlyOwnerCaller onlyInBadTimes returns(bool) {
        stopped = false;
        return true;
    }

    function stopInEmergency() public constant onlyInGoodTimes returns(bool) {
        return true;
    }

    function onlyInEmergency() public constant onlyInBadTimes returns(bool) {
        return true;
    }

    /*
     * Helper functions
     */

    function getAugur() public view returns (Augur) {
        return Augur(lookup("Augur"));
    }
}
