// Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE

pragma solidity ^0.4.13;

import 'ROOT/Controlled.sol';
import 'ROOT/libraries/trading/PlaceOrder.sol';
import 'ROOT/libraries/ReentrancyGuard.sol';
import 'ROOT/trading/IMakeOrder.sol';
import 'ROOT/trading/Trading.sol';

/**
 * @title MakeOrder
 * @dev This allows you to place orders on the book.
 */
contract MakeOrder is Controlled, ReentrancyGuard {
    using PlaceOrder for PlaceOrder.Data;

    function makeOrder(Trading.TradeTypes _type, uint256 _attoshares, int256 _displayPrice, IMarket _market, uint8 _outcome, bytes32 _betterOrderId, bytes32 _worseOrderId, uint256 _tradeGroupId) onlyInGoodTimes nonReentrant external returns (bytes32 _orderId) {
        PlaceOrder.Data memory _placeOrderData = PlaceOrder.create(controller, msg.sender, _outcome, _type, _attoshares, _displayPrice, _market, _betterOrderId, _worseOrderId, _tradeGroupId);

        uint256 _fxpMoneyEscrowed;
        uint256 _fxpSharesEscrowed;
        if (_placeOrderData.tradeType == Trading.TradeTypes.Ask) {
            (_fxpMoneyEscrowed, _fxpSharesEscrowed) = PlaceOrder.placeAsk(_placeOrderData);
        } else if (_placeOrderData.tradeType == Trading.TradeTypes.Bid) {
            (_fxpMoneyEscrowed, _fxpSharesEscrowed) = PlaceOrder.placeBid(_placeOrderData);
        }

        _orderId = _placeOrderData.orders.getOrderId(_placeOrderData.tradeType, _placeOrderData.market, _placeOrderData.attoshares, _placeOrderData.displayPrice, _placeOrderData.sender, block.number, _placeOrderData.outcome, _fxpMoneyEscrowed, _fxpSharesEscrowed);
        require(_placeOrderData.orders.getAmount(_orderId, _placeOrderData.tradeType, _placeOrderData.market, _placeOrderData.outcome) == 0);
        _orderId = _placeOrderData.orders.saveOrder(_orderId, _placeOrderData.tradeType, _placeOrderData.market, _placeOrderData.attoshares, _placeOrderData.displayPrice, _placeOrderData.sender, _placeOrderData.outcome, _fxpMoneyEscrowed, _fxpSharesEscrowed, _placeOrderData.betterOrderId, _placeOrderData.worseOrderId, _placeOrderData.tradeGroupId, tx.gasprice);

        return _orderId;
    }
}
