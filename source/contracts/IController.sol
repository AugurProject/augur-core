pragma solidity ^0.4.17;


contract IController {
    function assertIsWhitelisted(address _target) public constant returns(bool);
    function lookup(bytes32 _key) public constant returns(address);
    function assertOnlySpecifiedCaller(address _caller, bytes32 _allowedCaller) public constant returns(bool);
    function stopInEmergency() constant returns(bool);
    function onlyInEmergency() constant returns(bool);
}
