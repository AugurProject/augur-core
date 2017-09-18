// Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE

pragma solidity ^0.4.13;

import 'ROOT/Controlled.sol';
import 'ROOT/libraries/ReentrancyGuard.sol';
import 'ROOT/trading/Order.sol';
import 'ROOT/reporting/IMarket.sol';
import 'ROOT/trading/IMakeOrder.sol';
import 'ROOT/trading/IOrders.sol';
import 'ROOT/trading/ITakeOrder.sol';


contract Trade is Controlled, ReentrancyGuard {
    uint256 private constant MINIMUM_GAS_NEEDED = 300000;

    function publicBuy(IMarket _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupId) external onlyInGoodTimes nonReentrant returns (bytes32) {
        return trade(msg.sender, Order.TradeDirections.Long, _market, _outcome, _fxpAmount, _fxpPrice, _tradeGroupId);
    }

    function publicSell(IMarket _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupId) external onlyInGoodTimes nonReentrant returns (bytes32) {
        return trade(msg.sender, Order.TradeDirections.Short, _market, _outcome, _fxpAmount, _fxpPrice, _tradeGroupId);
    }

    function publicTrade(Order.TradeDirections _direction, IMarket _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupId) external onlyInGoodTimes nonReentrant returns (bytes32) {
        return trade(msg.sender, _direction, _market, _outcome, _fxpAmount, _fxpPrice, _tradeGroupId);
    }

    function publicTakeBestOrder(Order.TradeDirections _direction, IMarket _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupId) external onlyInGoodTimes nonReentrant returns (uint256) {
        return takeBestOrder(msg.sender, _direction, _market, _outcome, _fxpAmount, _fxpPrice, _tradeGroupId);
    }

    // CONSIDER: We may want to return multiple values here to indicate success and the order id seperately.
    function trade(address _sender, Order.TradeDirections _direction, IMarket _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupId) internal returns (bytes32) {
        uint256 _bestFxpAmount = takeBestOrder(_sender, _direction, _market, _outcome, _fxpAmount, _fxpPrice, _tradeGroupId);
        if (_bestFxpAmount == 0) {
            return bytes32(1);
        }
        if (msg.gas < MINIMUM_GAS_NEEDED) {
            return bytes32(1);
        }
        Order.TradeTypes _type = Order.getOrderTradingTypeFromMakerDirection(_direction);
        return IMakeOrder(controller.lookup("MakeOrder")).makeOrder(_sender, _type, _bestFxpAmount, _fxpPrice, _market, _outcome, 0, 0, _tradeGroupId);
    }

    function takeBestOrder(address _sender, Order.TradeDirections _direction, IMarket _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupId) internal returns (uint256 _bestFxpAmount) {
        // we need to take a BID if we want to SELL and we need to take an ASK if we want to BUY
        Order.TradeTypes _type = Order.getOrderTradingTypeFromTakerDirection(_direction);
        IOrders _orders = IOrders(controller.lookup("Orders"));
        bytes32 _orderId = _orders.getBestOrderId(_type, _market, _outcome);
        _bestFxpAmount = _fxpAmount;
        while (_orderId != 0 && _bestFxpAmount > 0 && msg.gas >= MINIMUM_GAS_NEEDED) {
            int256 _fxpOrderPrice = _orders.getPrice(_orderId);
            // If the price is acceptable relative to the trade type
            if (_type == Order.TradeTypes.Bid ? _fxpOrderPrice >= _fxpPrice : _fxpOrderPrice <= _fxpPrice) {
                _orders.setPrice(_market, _outcome, _fxpOrderPrice);
                bytes32 _nextOrderId = _orders.getWorseOrderId(_orderId);
                if (_orders.getOrderMaker(_orderId) != _sender) {
                    _bestFxpAmount = ITakeOrder(controller.lookup("TakeOrder")).takeOrder(_sender, _orderId, _bestFxpAmount, _tradeGroupId);
                }
                _orderId = _nextOrderId;
            } else {
                _orderId = bytes32(0);
            }
        }
        return _bestFxpAmount;
    }
}
