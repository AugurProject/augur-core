pragma solidity ^0.4.13;

import 'ROOT/reporting/IMarket.sol';
import 'ROOT/trading/Trading.sol';


contract IOrdersFetcher {
    function getOrderIds(Trading.TradeTypes _type, IMarket _market, uint8 _outcome, bytes32 _startingOrderId, uint256 _numOrdersToLoad) external constant returns (bytes32[]);
    function getOrder(bytes32 _orderId) public constant returns (uint256 _attoshares, int256 _displayPrice, address _owner, uint256 _tokensEscrowed, uint256 _sharesEscrowed, bytes32 _betterOrderId, bytes32 _worseOrderId, uint256 _gasPrice);
    function findBoundingOrders(Trading.TradeTypes _type, IMarket _market, uint8 _outcome, int256 _fxpPrice, bytes32 _bestOrderId, bytes32 _worstOrderId, bytes32 _betterOrderId, bytes32 _worseOrderId) public constant returns (bytes32, bytes32);
}
