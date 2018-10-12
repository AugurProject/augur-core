pragma solidity 0.4.24;

import 'IAugur.sol';


contract IController {
    address public owner;
    bool public useAuction;
    function assertIsWhitelisted(address _target) public view returns(bool);
    function lookup(bytes32 _key) public view returns(address);
    function getAugur() public view returns (IAugur);
    function getTimestamp() public view returns (uint256);
}
