pragma solidity 0.4.24;


import 'trading/Order.sol';


contract IFillOrder {
    function publicFillOrder(bytes32 _orderId, uint256 _amountFillerWants, bytes32 _tradeGroupId) external payable returns (uint256);
    function fillOrder(address _filler, bytes32 _orderId, uint256 _amountFillerWants, bytes32 tradeGroupId) external returns (uint256);
}
