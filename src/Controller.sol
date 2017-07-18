contract Controlled
{
	bool private initialized = false;
	address public owner;
	Controller internal controller;

	modifier whitelistOnly
	{
		controller.assertIsWhitelisted(msg.sender);
		_;
	}

	modifier controllerOnly
	{
		require(Controller(msg.sender) == controller);
		_;
	}

	modifier ownerOnly
	{
		require(msg.sender == owner);
		_;
	}

	function Controlled()
	{
		owner = msg.sender;
	}

	// TODO: convert into constructor call
	function initialize(Controller _controller) external ownerOnly returns(bool)
	{
		require(initialized == false);
		initialized = true;
		controller = _controller;
		owner = address(0);
		return true;
	}

	function setController(Controller _controller) public controllerOnly returns(bool)
	{
		controller = _controller;
		return true;
	}

	function suicideFunds(address _target) public controllerOnly returns(bool)
	{
		selfdestruct(_target);
		return true;
	}
}

contract Controller
{
	address public owner;
	mapping(address => bool) public whitelist;
	mapping(bytes32 => address) public registry;
	bool public stopped = false;

	modifier whitelistOnly
	{
		assertIsWhitelisted(msg.sender);
		_;
	}

	modifier devModeOwnerOnly
	{
		require(msg.sender == owner);
		require(whitelist[owner]);
		_;
	}

	modifier ownerOnly
	{
		require(msg.sender == owner);
		_;
	}

	modifier onlyInBadTimes
	{
		require(stopped);
		_;
	}

	modifier onlyInGoodTimes
	{
		require(!stopped);
		_;
	}

	function Controller()
	{
		owner = msg.sender;
		whitelist[owner] = true;
	}

	function foo() public returns(bool)
	{
		return true;
	}

	/*
	 * Whitelisting [whitelisted augur contracts and dev mode can use it]
	 */

	function addToWhitelist(address _target) public whitelistOnly returns(bool)
	{
		whitelist[_target] = true;
		return true;
	}

	function removeFromWhitelist(address _target) public whitelistOnly returns(bool)
	{
		whitelist[_target] = false;
		return true;
	}

	function assertIsWhitelisted(address _target) public returns(bool)
	{
		require(whitelist[_target]);
		return true;
	}

	/*
	 * Registry for lookups [whitelisted augur contracts and dev mode can use it]
	 */

	function setValue(bytes32 _key, address _value) public whitelistOnly returns(bool)
	{
		registry[_key] = _value;
		return true;
	}

	function lookup(bytes32 _key) public returns(address)
	{
		return registry[_key];
	}

	function assertOnlySpecifiedCaller(address _caller, bytes32 _allowedCaller) public returns(bool)
	{
		require(registry[_allowedCaller] == _caller || (msg.sender == owner && whitelist[owner]));
		return true;
	}

	/*
	 * Contract Administration [dev mode can use it]
	 */

	function suicide(Controlled _target, address _destination) public devModeOwnerOnly returns(bool)
	{
		_target.suicideFunds(_destination);
		return true;
	}

	function updateController(Controlled _target, Controller _newController) public devModeOwnerOnly returns(bool)
	{
		_target.setController(_newController);
		return true;
	}

	 /*
	 * Controller Administration [dev can transfer ownership anytime, mode can only switched from dev mode -> decentralized]
	 */

	function transferOwnership(address _newOwner) ownerOnly returns(bool)
	{
		// if in dev mode, blacklist old owner and whitelist new owner
		if (whitelist[owner])
		{
			whitelist[owner] = false;
			whitelist[_newOwner] = true;
		}
		owner = _newOwner;
		return true;
	}

	function switchModeSoOnlyEmergencyStopsAndEscapeHatchesCanBeUsed() public devModeOwnerOnly returns(bool)
	{
		whitelist[owner] = false;
		return true;
	}

	/*
	 * Emergency Stop Functions [dev can use it anytime in or out of dev mode]
	 */

	function emergencyStop() public ownerOnly onlyInGoodTimes returns(bool)
	{
		stopped = true;
		return true;
	}

	function release() public ownerOnly onlyInBadTimes returns(bool)
	{
		stopped = false;
		return true;
	}

	function stopInEmergency() public onlyInGoodTimes returns(bool)
	{
		return true;
	}

	function onlyInEmergency() public onlyInBadTimes returns(bool)
	{
		return true;
	}
}
