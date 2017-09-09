pragma solidity ^0.4.13;

import 'ROOT/trading/Order.sol';


contract ITakeOrder {
    function publicTakeOrder(bytes32 _orderId, uint256 _amountTakerWants, uint256 _tradeGroupId) external returns (uint256);
    function takeOrder(address _taker, bytes32 _orderId, uint256 _amountTakerWants, uint256 tradeGroupId) external returns (uint256);
}
