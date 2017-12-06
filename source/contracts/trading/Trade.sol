// Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE

pragma solidity 0.4.18;


import 'Controlled.sol';
import 'libraries/ReentrancyGuard.sol';
import 'trading/Order.sol';
import 'reporting/IMarket.sol';
import 'trading/ICreateOrder.sol';
import 'trading/IOrders.sol';
import 'trading/IFillOrder.sol';
import 'libraries/CashAutoConverter.sol';
import 'libraries/Extractable.sol';


contract Trade is CashAutoConverter, Extractable, ReentrancyGuard {
    uint256 private constant MINIMUM_GAS_NEEDED = 500000;

    function publicBuy(IMarket _market, uint8 _outcome, uint256 _fxpAmount, uint256 _price, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId) external payable convertToAndFromCash onlyInGoodTimes nonReentrant returns (bytes32) {
        return trade(msg.sender, Order.TradeDirections.Long, _market, _outcome, _fxpAmount, _price, _betterOrderId, _worseOrderId, _tradeGroupId);
    }

    function publicSell(IMarket _market, uint8 _outcome, uint256 _fxpAmount, uint256 _price, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId) external payable convertToAndFromCash onlyInGoodTimes nonReentrant returns (bytes32) {
        return trade(msg.sender, Order.TradeDirections.Short, _market, _outcome, _fxpAmount, _price, _betterOrderId, _worseOrderId, _tradeGroupId);
    }

    function publicTrade(Order.TradeDirections _direction, IMarket _market, uint8 _outcome, uint256 _fxpAmount, uint256 _price, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId) external payable convertToAndFromCash onlyInGoodTimes nonReentrant returns (bytes32) {
        return trade(msg.sender, _direction, _market, _outcome, _fxpAmount, _price, _betterOrderId, _worseOrderId, _tradeGroupId);
    }

    function publicTakeBestOrder(Order.TradeDirections _direction, IMarket _market, uint8 _outcome, uint256 _fxpAmount, uint256 _price, bytes32 _tradeGroupId) external payable convertToAndFromCash onlyInGoodTimes nonReentrant returns (uint256) {
        return fillBestOrder(msg.sender, _direction, _market, _outcome, _fxpAmount, _price, _tradeGroupId);
    }

    // CONSIDER: We may want to return multiple values here to indicate success and the order id seperately.
    function trade(address _sender, Order.TradeDirections _direction, IMarket _market, uint8 _outcome, uint256 _fxpAmount, uint256 _price, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId) internal returns (bytes32) {
        uint256 _bestFxpAmount = fillBestOrder(_sender, _direction, _market, _outcome, _fxpAmount, _price, _tradeGroupId);
        if (_bestFxpAmount == 0) {
            return bytes32(1);
        }
        if (msg.gas < MINIMUM_GAS_NEEDED) {
            return bytes32(1);
        }
        Order.Types _type = Order.getOrderTradingTypeFromMakerDirection(_direction);
        return ICreateOrder(controller.lookup("CreateOrder")).createOrder(_sender, _type, _bestFxpAmount, _price, _market, _outcome, _betterOrderId, _worseOrderId, _tradeGroupId);
    }

    function fillBestOrder(address _sender, Order.TradeDirections _direction, IMarket _market, uint8 _outcome, uint256 _fxpAmount, uint256 _price, bytes32 _tradeGroupId) internal returns (uint256 _bestFxpAmount) {
        // we need to fill a BID if we want to SELL and we need to fill an ASK if we want to BUY
        Order.Types _type = Order.getOrderTradingTypeFromFillerDirection(_direction);
        IOrders _orders = IOrders(controller.lookup("Orders"));
        bytes32 _orderId = _orders.getBestOrderId(_type, _market, _outcome);
        _bestFxpAmount = _fxpAmount;
        while (_orderId != 0 && _bestFxpAmount > 0 && msg.gas >= MINIMUM_GAS_NEEDED) {
            uint256 _orderPrice = _orders.getPrice(_orderId);
            // If the price is acceptable relative to the trade type
            if (_type == Order.Types.Bid ? _orderPrice >= _price : _orderPrice <= _price) {
                _orders.setPrice(_market, _outcome, _orderPrice);
                bytes32 _nextOrderId = _orders.getWorseOrderId(_orderId);
                if (_orders.getOrderCreator(_orderId) != _sender) {
                    _bestFxpAmount = IFillOrder(controller.lookup("FillOrder")).fillOrder(_sender, _orderId, _bestFxpAmount, _tradeGroupId);
                }
                _orderId = _nextOrderId;
            } else {
                _orderId = bytes32(0);
            }
        }
        return _bestFxpAmount;
    }

    function getProtectedTokens() internal returns (address[] memory) {
        return new address[](0);
    }
}
