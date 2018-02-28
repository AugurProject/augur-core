pragma solidity ^0.4.20;

import 'libraries/DelegationTarget.sol';
import 'libraries/ITyped.sol';


contract DelegatorHelper is DelegationTarget, ITyped {
    string public stringMember = "StringMember";
    string public stringConstant = "StringConstant";
    int256 public intValue = -42;
    bytes32 public name = "Name";
    bytes32 private privateName = "PrivateName";
    bytes32 constant public constantName = "ConstantName";
    mapping(uint256 => uint256) public map;
    uint256[] public uint256Array;
    DelegatorHelper private otherContract;

    function getTypeName() public view returns (bytes32) {
        return "DelegatorHelper";
    }

    function setStringMember(string _value) public returns (bool) {
        stringMember = _value;
        return true;
    }

    function populateStringMember() public returns (bool) {
        stringMember = "Value";
        return true;
    }

    function setName(bytes32 _name) public returns (bool) {
        name = _name;
        return true;
    }

    function setIntValue(int256 _value) public returns (bool) {
        intValue = _value;
        return true;
    }

    function setPrivateName(bytes32 _name) public returns (bool) {
        privateName = _name;
        return true;
    }

    function pushArrayValue(uint256 _value) public returns (bool) {
        uint256Array.push(_value);
        return true;
    }

    function addToMap(uint256 _key, uint256 _value) public returns (bool) {
        map[_key] = _value;
        return true;
    }

    function setOtherContract(DelegatorHelper _other) public returns (bool) {
        otherContract = _other;
        return true;
    }

    function getStringMember() public view returns (string) {
        return stringMember;
    }

    function getStringConstant() public view returns (string) {
        return stringConstant;
    }

    function getName() public view returns (bytes32) {
        return name;
    }

    function getIntValue() public view returns (int256) {
        return intValue;
    }

    function getPrivateName() public view returns (bytes32) {
        return privateName;
    }

    function getConstantName() public view returns (bytes32) {
        return constantName;
    }

    function getMapValue(uint256 _key) public view returns (uint256) {
        return map[_key];
    }

    function getArrayValue(uint256 _index) public view returns (uint256) {
        return uint256Array[_index];
    }

    function getArraySize() public view returns (uint256) {
        return uint256Array.length;
    }

    function getOtherName() public view returns (bytes32) {
        return otherContract.name();
    }

    function addToOtherMap(uint256 _key, uint256 _value) public returns (bool) {
        return otherContract.addToMap(_key, _value);
    }

    function getOtherMapValue(uint256 _key) public returns (uint256) {
        return otherContract.getMapValue(_key);
    }

    function noInputReturn() public returns (uint256) {
        return 1;
    }

    function manyInputsNoReturn(uint256 _one, uint256 _two, uint256 _three, uint256 _four) public {
        return;
    }

    function returnDynamic() public returns (uint256[]) {
        uint256[] memory _retval = new uint256[](5);
        _retval[0] = 1;
        return _retval;
    }

    function returnFixed() public returns (uint256[5] _retval) {
        _retval[0] = 1;
        return _retval;
    }
}
