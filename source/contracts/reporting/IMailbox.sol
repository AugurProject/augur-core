pragma solidity 0.4.20;

import 'reporting/IMarket.sol';


contract IMailbox {
    function initialize(address _owner, IMarket _market) public returns (bool);
    function depositEther() public payable returns (bool);
}
