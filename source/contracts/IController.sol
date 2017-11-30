pragma solidity 0.4.18;

import 'Augur.sol';


contract IController {
    function assertIsWhitelisted(address _target) public view returns(bool);
    function lookup(bytes32 _key) public view returns(address);
    function assertOnlySpecifiedCaller(address _caller, bytes32 _allowedCaller) public view returns(bool);
    function stopInEmergency() public view returns(bool);
    function onlyInEmergency() public view returns(bool);
    function getAugur() public view returns (Augur);
    function getTimestamp() public view returns (uint256);
}
