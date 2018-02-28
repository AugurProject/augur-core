pragma solidity 0.4.20;


import 'trading/Order.sol';
import 'reporting/IMarket.sol';


contract IOrdersFetcher {
    function findBoundingOrders(Order.Types _type, uint256 _price, bytes32 _bestOrderId, bytes32 _worstOrderId, bytes32 _betterOrderId, bytes32 _worseOrderId) public returns (bytes32, bytes32);
}
