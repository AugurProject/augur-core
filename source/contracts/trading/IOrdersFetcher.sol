pragma solidity ^0.4.17;

import 'trading/Order.sol';
import 'reporting/IMarket.sol';


contract IOrdersFetcher {
    function getOrder(bytes32 _orderId) public constant returns (uint256 _attoshares, uint256 _displayPrice, address _owner, uint256 _tokensEscrowed, uint256 _sharesEscrowed, bytes32 _betterOrderId, bytes32 _worseOrderId, uint256 _gasPrice);
    function findBoundingOrders(Order.TradeTypes _type, uint256 _price, bytes32 _bestOrderId, bytes32 _worstOrderId, bytes32 _betterOrderId, bytes32 _worseOrderId) public constant returns (bytes32, bytes32);
}
