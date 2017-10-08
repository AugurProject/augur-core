pragma solidity 0.4.17;


import 'libraries/token/ERC20.sol';


contract ICash is ERC20 {
    function depositEther() external payable returns(bool);
    function depositEtherFor(address _to) external payable returns(bool);
    function withdrawEther(uint256 _amount) external returns(bool);
    function withdrawEtherTo(address _to, uint256 _amount) external returns(bool);
    function getTypeName() constant returns (bytes32);
}
