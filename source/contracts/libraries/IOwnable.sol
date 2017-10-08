pragma solidity 0.4.17;
pragma experimental ABIEncoderV2;
pragma experimental "v0.5.0";


contract IOwnable {
    function getOwner() public constant returns (address);
    function transferOwnership(address newOwner) public returns (bool);
}
