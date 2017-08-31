pragma solidity ^0.4.13;


contract Controlled {
    Controller public controller;

    modifier onlyWhitelistedCallers {
        require(controller.assertIsWhitelisted(msg.sender));
        _;
    }

    modifier onlyControllerCaller {
        require(Controller(msg.sender) == controller);
        _;
    }

    modifier onlyInGoodTimes {
        require(controller.stopInEmergency());
        _;
    }

    modifier onlyInBadTimes {
        require(controller.onlyInEmergency());
        _;
    }

    function Controlled() {
        controller = Controller(msg.sender);
    }

    function setController(Controller _controller) public onlyControllerCaller returns(bool) {
        controller = _controller;
        return true;
    }

    function suicideFunds(address _target) public onlyControllerCaller returns(bool) {
        selfdestruct(_target);
        return true;
    }
}


contract Controller {
    address public owner;
    mapping(address => bool) public whitelist;
    mapping(bytes32 => address) public registry;
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

    function Controller() {
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

    function assertIsWhitelisted(address _target) constant returns(bool) {
        require(whitelist[_target]);
        return true;
    }

    /*
     * Registry for lookups [whitelisted augur contracts and dev mode can use it]
     */

    function setValue(bytes32 _key, address _value) public onlyWhitelistedCallers returns(bool) {
        registry[_key] = _value;
        return true;
    }

    function removeValue(bytes32 _key) public onlyWhitelistedCallers returns(bool) {
        registry[_key] = address(0);
        return true;
    }

    function lookup(bytes32 _key) constant returns(address) {
        return registry[_key];
    }

    function assertOnlySpecifiedCaller(address _caller, bytes32 _allowedCaller) constant returns(bool) {
        require(registry[_allowedCaller] == _caller || (msg.sender == owner && whitelist[owner]));
        return true;
    }

    /*
     * Contract Administration [dev mode can use it]
     */

    function suicide(Controlled _target, address _destination) public devModeOwnerOnly returns(bool) {
        _target.suicideFunds(_destination);
        return true;
    }

    function updateController(Controlled _target, Controller _newController) public devModeOwnerOnly returns(bool) {
        _target.setController(_newController);
        return true;
    }

     /*
     * Controller Administration [dev can transfer ownership anytime, mode can only switched from dev mode -> decentralized]
     */

    function transferOwnership(address _newOwner) onlyOwnerCaller returns(bool) {
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

    function stopInEmergency() constant onlyInGoodTimes returns(bool) {
        return true;
    }

    function onlyInEmergency() constant onlyInBadTimes returns(bool) {
        return true;
    }
}
