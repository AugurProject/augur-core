pragma solidity 0.4.17;


import 'trading/Order.sol';
import 'reporting/IMarket.sol';


contract IOrders {
    function saveOrder(Order.OrderTypes _type, IMarket _market, uint256 _fxpAmount, uint256 _price, address _sender, uint8 _outcome, uint256 _moneyEscrowed, uint256 _sharesEscrowed, bytes32 _betterOrderId, bytes32 _worseOrderId, uint256 _tradeGroupId) public returns (bytes32 _orderId);
    function removeOrder(bytes32 _orderId) public returns (bool);
    function getMarket(bytes32 _orderId) public view returns (IMarket);
    function getOrderType(bytes32 _orderId) public view returns (Order.OrderTypes);
    function getOutcome(bytes32 _orderId) public view returns (uint8);
    function getAmount(bytes32 _orderId) public view returns (uint256);
    function getPrice(bytes32 _orderId) public view returns (uint256);
    function getOrderCreator(bytes32 _orderId) public view returns (address);
    function getOrderSharesEscrowed(bytes32 _orderId) public view returns (uint256);
    function getOrderMoneyEscrowed(bytes32 _orderId) public view returns (uint256);
    function getBetterOrderId(bytes32 _orderId) public view returns (bytes32);
    function getWorseOrderId(bytes32 _orderId) public view returns (bytes32);
    function getBestOrderId(Order.OrderTypes _type, IMarket _market, uint8 _outcome) public view returns (bytes32);
    function getWorstOrderId(Order.OrderTypes _type, IMarket _market, uint8 _outcome) public view returns (bytes32);
    function getLastOutcomePrice(IMarket _market, uint8 _outcome) public view returns (uint256);
    function getOrderId(Order.OrderTypes _type, IMarket _market, uint256 _fxpAmount, uint256 _price, address _sender, uint256 _blockNumber, uint8 _outcome, uint256 _moneyEscrowed, uint256 _sharesEscrowed) public view returns (bytes32);
    function isBetterPrice(Order.OrderTypes _type, uint256 _price, bytes32 _orderId) public view returns (bool);
    function isWorsePrice(Order.OrderTypes _type, uint256 _price, bytes32 _orderId) public view returns (bool);
    function assertIsNotBetterPrice(Order.OrderTypes _type, uint256 _price, bytes32 _betterOrderId) public view returns (bool);
    function assertIsNotWorsePrice(Order.OrderTypes _type, uint256 _price, bytes32 _worseOrderId) public returns (bool);
    function fillOrder(bytes32 _orderId, uint256 _sharesFilled, uint256 _tokensFilled) public returns (bool);
    function setPrice(IMarket _market, uint8 _outcome, uint256 _price) external returns (bool);
}
