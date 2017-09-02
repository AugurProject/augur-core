pragma solidity ^0.4.13;

import 'ROOT/libraries/token/ERC20.sol';


contract ICash is ERC20 {
    enum WithdrawState { Failed, Withdrawn, Initiated }
    function depositEther() external payable returns(bool);
    function withdrawEther(uint256 _amount) external returns(WithdrawState);
    function getMarket() constant returns (bool);
    function getTypeName() constant returns (bytes32);
}
