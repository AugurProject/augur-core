pragma solidity ^0.4.13;

import 'ROOT/trading/Order.sol';
import 'ROOT/reporting/IMarket.sol';


contract IOrdersFetcher {
    function getOrderIds(Order.TradeTypes _type, IMarket _market, uint8 _outcome, bytes32 _startingOrderId, uint256 _numOrdersToLoad) external constant returns (bytes32[]);
    function getOrder(bytes32 _orderId) public constant returns (uint256 _attoshares, uint256 _displayPrice, address _owner, uint256 _tokensEscrowed, uint256 _sharesEscrowed, bytes32 _betterOrderId, bytes32 _worseOrderId, uint256 _gasPrice);
    function findBoundingOrders(Order.TradeTypes _type, uint256 _fxpPrice, bytes32 _bestOrderId, bytes32 _worstOrderId, bytes32 _betterOrderId, bytes32 _worseOrderId) public constant returns (bytes32, bytes32);
}
