pragma solidity 0.4.17;



contract IOwnable {
    function getOwner() public constant returns (address);
    function transferOwnership(address newOwner) public returns (bool);
}
