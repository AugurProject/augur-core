pragma solidity 0.4.17;


import 'trading/Order.sol';
import 'reporting/IMarket.sol';


contract ICreateOrder {
    function publicCreateOrder(Order.OrderTypes, uint256, uint256, IMarket, uint8, bytes32, bytes32, uint256) external payable returns (bytes32);
    function createOrder(address, Order.OrderTypes, uint256, uint256, IMarket, uint8, bytes32, bytes32, uint256) external returns (bytes32);
}
