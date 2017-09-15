// Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE

pragma solidity ^0.4.13;

import 'ROOT/Controlled.sol';
import 'ROOT/libraries/ReentrancyGuard.sol';
import 'ROOT/trading/Order.sol';
import 'ROOT/trading/IMakeOrder.sol';


contract MakeOrder is Controlled, ReentrancyGuard {
    using Order for Order.Data;

    function publicMakeOrder(Order.TradeTypes _type, uint256 _attoshares, uint256 _displayPrice, IMarket _market, uint8 _outcome, bytes32 _betterOrderId, bytes32 _worseOrderId, uint256 _tradeGroupId) external onlyInGoodTimes nonReentrant returns (bytes32) {
        return this.makeOrder(msg.sender, _type, _attoshares, _displayPrice, _market, _outcome, _betterOrderId, _worseOrderId, _tradeGroupId);
    }

    function makeOrder(address _maker, Order.TradeTypes _type, uint256 _attoshares, uint256 _displayPrice, IMarket _market, uint8 _outcome, bytes32 _betterOrderId, bytes32 _worseOrderId, uint256 _tradeGroupId) public onlyWhitelistedCallers returns (bytes32) {
        Order.Data memory _orderData = Order.create(controller, _maker, _outcome, _type, _attoshares, _displayPrice, _market, _betterOrderId, _worseOrderId);
        Order.escrowFunds(_orderData);
        require(_orderData.orders.getAmount(_orderData.getOrderId()) == 0);

        return Order.saveOrder(_orderData, _tradeGroupId);
    }
}
