pragma solidity ^0.4.13;

import 'trading/Order.sol';


contract IFillOrder {
    function publicFillOrder(bytes32 _orderId, uint256 _amountTakerWants, uint256 _tradeGroupId) external payable returns (uint256);
    function fillOrder(address _taker, bytes32 _orderId, uint256 _amountTakerWants, uint256 tradeGroupId) external returns (uint256);
}
