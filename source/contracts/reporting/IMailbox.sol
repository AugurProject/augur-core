pragma solidity 0.4.20;


contract IMailbox {
    function initialize(address _owner) public returns (bool);
    function depositEther() public payable returns (bool);
}
