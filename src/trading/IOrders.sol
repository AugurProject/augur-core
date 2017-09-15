pragma solidity ^0.4.13;

import 'ROOT/trading/Order.sol';
import 'ROOT/reporting/IMarket.sol';


contract IOrders {
    function saveOrder(Order.TradeTypes _type, IMarket _market, uint256 _fxpAmount, uint256 _fxpPrice, address _sender, uint8 _outcome, uint256 _fxpMoneyEscrowed, uint256 _fxpSharesEscrowed, bytes32 _betterOrderId, bytes32 _worseOrderId, uint256 _tradeGroupId) public returns (bytes32 _orderId);
    function removeOrder(bytes32 _orderId) public returns (bool);
    function getOrders(bytes32 _orderId) public constant returns (uint256 _amount, uint256 _price, address _owner, uint256 _sharesEscrowed, uint256 _tokensEscrowed, bytes32 _betterOrderId, bytes32 _worseOrderId);
    function getMarket(bytes32 _orderId) public constant returns (IMarket);
    function getTradeType(bytes32 _orderId) public constant returns (Order.TradeTypes);
    function getOutcome(bytes32 _orderId) public constant returns (uint8);
    function getAmount(bytes32 _orderId) public constant returns (uint256);
    function getPrice(bytes32 _orderId) public constant returns (uint256);
    function getOrderMaker(bytes32 _orderId) public constant returns (address);
    function getOrderSharesEscrowed(bytes32 _orderId) public constant returns (uint256);
    function getOrderMoneyEscrowed(bytes32 _orderId) public constant returns (uint256);
    function getBetterOrderId(bytes32 _orderId) public constant returns (bytes32);
    function getWorseOrderId(bytes32 _orderId) public constant returns (bytes32);
    function getBestOrderId(Order.TradeTypes _type, IMarket _market, uint8 _outcome) public constant returns (bytes32);
    function getWorstOrderId(Order.TradeTypes _type, IMarket _market, uint8 _outcome) public constant returns (bytes32);
    function getOrderId(Order.TradeTypes _type, IMarket _market, uint256 _fxpAmount, uint256 _fxpPrice, address _sender, uint256 _blockNumber, uint8 _outcome, uint256 _fxpMoneyEscrowed, uint256 _fxpSharesEscrowed) public constant returns (bytes32);
    function isBetterPrice(Order.TradeTypes _type, uint256 _fxpPrice, bytes32 _orderId) public constant returns (bool);
    function isWorsePrice(Order.TradeTypes _type, uint256 _fxpPrice, bytes32 _orderId) public constant returns (bool);
    function assertIsNotBetterPrice(Order.TradeTypes _type, uint256 _fxpPrice, bytes32 _betterOrderId) public constant returns (bool);
    function assertIsNotWorsePrice(Order.TradeTypes _type, uint256 _fxpPrice, bytes32 _worseOrderId) public returns (bool);
    function fillOrder(bytes32 _orderId, uint256 _sharesFilled, uint256 _tokensFilled) public returns (bool);
    function buyCompleteSetsLog(address _sender, IMarket _market, uint256 _fxpAmount, uint256 _numOutcomes) public constant returns (bool);
    function sellCompleteSetsLog(address _sender, IMarket _market, uint256 _fxpAmount, uint256 _numOutcomes, uint256 _marketCreatorFee, uint256 _reportingFee) public constant returns (bool);
    function cancelOrderLog(bytes32 _orderId) public constant returns (bool);
    function takeOrderLog(bytes32 _orderId, address _taker, uint256 _makerSharesFilled, uint256 _makerTokensFilled, uint256 _takerSharesFilled, uint256 _takerTokensFilled, uint256 _tradeGroupId) public constant returns (bool);
    function modifyMarketVolume(IMarket _market, uint256 _fxpAmount) external returns (bool);
    function setPrice(IMarket _market, uint8 _outcome, uint256 _fxpPrice) external returns (bool);
}
