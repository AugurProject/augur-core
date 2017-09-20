pragma solidity ^0.4.13;

import 'ROOT/libraries/token/ERC20.sol';


contract ICash is ERC20 {
    function depositEther() external payable returns(bool);
    function depositEtherFor(address _to) public payable returns(bool);
    function withdrawEther(uint256 _amount) external returns(bool);
    function withdrawEtherTo(address _to, uint256 _amount) public returns(bool);
    function getTypeName() constant returns (bytes32);
}
