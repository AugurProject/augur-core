// Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE

pragma solidity ^0.4.13;

import 'ROOT/Controlled.sol';
import 'ROOT/libraries/ReentrancyGuard.sol';
import 'ROOT/reporting/IMarket.sol';
import 'ROOT/trading/IOrders.sol';
import 'ROOT/trading/Trading.sol';


// FIXME: Remove this once MakeOrder is implemented in Solidity
contract IMakeOrder {
    function makeOrder(address, Trading.TradeDirections, uint256, int256, IMarket, uint8, bytes32, bytes32, uint256) returns (bytes32);
}


// FIXME: Remove this once TakeOrder is implemented in Solidity
contract ITakeOrder {
    function takeOrder(address, bytes32, Trading.TradeTypes, IMarket, uint8, uint256, uint256) returns (uint256);
}


contract Trade is Controlled, ReentrancyGuard {
    uint256 private constant MINIMUM_GAS_NEEDED = 300000;

    function publicBuy(IMarket _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupId) external onlyInGoodTimes nonReentrant returns (bytes32) {
        return trade(msg.sender, Trading.TradeDirections.Buying, _market, _outcome, _fxpAmount, _fxpPrice, _tradeGroupId);
    }

    function publicSell(IMarket _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupId) external onlyInGoodTimes nonReentrant returns (bytes32) {
        return trade(msg.sender, Trading.TradeDirections.Selling, _market, _outcome, _fxpAmount, _fxpPrice, _tradeGroupId);
    }

    function publicTrade(Trading.TradeDirections _direction, IMarket _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupId) external onlyInGoodTimes nonReentrant returns (bytes32) {
        return trade(msg.sender, _direction, _market, _outcome, _fxpAmount, _fxpPrice, _tradeGroupId);
    }

    function publicTakeBestOrder(Trading.TradeDirections _direction, IMarket _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupId) external onlyInGoodTimes nonReentrant returns (uint256) {
        return takeBestOrder(msg.sender, _direction, _market, _outcome, _fxpAmount, _fxpPrice, _tradeGroupId);
    }

    // CONSIdER: We may want to return multiple values here to indicate success and the order id seperately.
    function trade(address _sender, Trading.TradeDirections _direction, IMarket _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupId) internal returns (bytes32) {
        uint256 _bestFxpAmount = takeBestOrder(_sender, _direction, _market, _outcome, _fxpAmount, _fxpPrice, _tradeGroupId);
        if (_bestFxpAmount == 0) {
            return bytes32(1);
        }
        if (msg.gas < MINIMUM_GAS_NEEDED) {
            return bytes32(1);
        }
        return IMakeOrder(controller.lookup("makeOrder")).makeOrder(_sender, _direction, _bestFxpAmount, _fxpPrice, _market, _outcome, 0, 0, _tradeGroupId);
    }

    function takeBestOrder(address _sender, Trading.TradeDirections _direction, IMarket _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupId) internal returns (uint256 _bestFxpAmount) {
        // we need to take a BId if we want to SELL and we need to take an ASK if we want to BUY
        Trading.TradeTypes _type = (_direction == Trading.TradeDirections.Selling) ? Trading.TradeTypes.Bid : Trading.TradeTypes.Ask;
        IOrders _orders = IOrders(controller.lookup("Orders"));
        bytes32 _orderId = _orders.getBestOrderId(_type, _market, _outcome);
        _bestFxpAmount = _fxpAmount;
        while (_orderId != 0 && _bestFxpAmount > 0 && msg.gas >= MINIMUM_GAS_NEEDED) {
            int256 _fxpOrderPrice = _orders.getPrice(_orderId, _type, _market, _outcome);
            // If the price is acceptable relative to the trade type
            if (_type == Trading.TradeTypes.Bid ? _fxpOrderPrice >= _fxpPrice : _fxpOrderPrice <= _fxpPrice) {
                _orders.setPrice(_market, _outcome, _fxpOrderPrice);
                _orders.modifyMarketVolume(_market, _bestFxpAmount);
                bytes32 _nextOrderId = _orders.getWorseOrderId(_orderId, _type, _market, _outcome);
                if (_orders.getOrderOwner(_orderId, _type, _market, _outcome) != _sender) {
                    _bestFxpAmount = ITakeOrder(controller.lookup("takeOrder")).takeOrder(_sender, _orderId, _type, _market, _outcome, _bestFxpAmount, _tradeGroupId);
                }
                _orderId = _nextOrderId;
            } else {
                _orderId = 0;
            }
        }
        return _bestFxpAmount;
    }
}
