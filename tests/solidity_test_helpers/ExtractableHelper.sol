pragma solidity ^0.4.18;

import 'libraries/Extractable.sol';


contract ExtractableHelper is Extractable {
    address[] private protectedTokens;

    function deposit() public payable { }

    function setProtectedToken(address _protectedToken) public returns (bool) {
        protectedTokens.push(_protectedToken);
        return true;
    }

    function getProtectedTokens() internal returns (address[] memory) {
        return protectedTokens;
    }
}
