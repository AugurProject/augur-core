// Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE

pragma solidity 0.4.24;


import 'Controlled.sol';
import 'libraries/ReentrancyGuard.sol';
import 'libraries/MarketValidator.sol';
import 'trading/Order.sol';
import 'reporting/IMarket.sol';
import 'trading/ICreateOrder.sol';
import 'trading/IOrders.sol';
import 'trading/IFillOrder.sol';
import 'libraries/CashAutoConverter.sol';


contract Trade is CashAutoConverter, ReentrancyGuard, MarketValidator {
    function publicBuy(IMarket _market, uint256 _outcome, uint256 _fxpAmount, uint256 _price, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId, uint256 _loopLimit) external payable marketIsLegit(_market) convertToAndFromCash returns (bytes32) {
        bytes32 _result = trade(msg.sender, Order.TradeDirections.Long, _market, _outcome, _fxpAmount, _price, _betterOrderId, _worseOrderId, _tradeGroupId, _loopLimit);
        _market.assertBalances();
        return _result;
    }

    function publicSell(IMarket _market, uint256 _outcome, uint256 _fxpAmount, uint256 _price, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId, uint256 _loopLimit) external payable marketIsLegit(_market) convertToAndFromCash returns (bytes32) {
        bytes32 _result = trade(msg.sender, Order.TradeDirections.Short, _market, _outcome, _fxpAmount, _price, _betterOrderId, _worseOrderId, _tradeGroupId, _loopLimit);
        _market.assertBalances();
        return _result;
    }

    function publicTrade(Order.TradeDirections _direction, IMarket _market, uint256 _outcome, uint256 _fxpAmount, uint256 _price, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId, uint256 _loopLimit) external payable marketIsLegit(_market) convertToAndFromCash returns (bytes32) {
        bytes32 _result = trade(msg.sender, _direction, _market, _outcome, _fxpAmount, _price, _betterOrderId, _worseOrderId, _tradeGroupId, _loopLimit);
        _market.assertBalances();
        return _result;
    }

    function publicFillBestOrder(Order.TradeDirections _direction, IMarket _market, uint256 _outcome, uint256 _fxpAmount, uint256 _price, bytes32 _tradeGroupId, uint256 _loopLimit) external payable marketIsLegit(_market) convertToAndFromCash returns (uint256) {
        uint256 _result = fillBestOrder(msg.sender, _direction, _market, _outcome, _fxpAmount, _price, _tradeGroupId, _loopLimit);
        _market.assertBalances();
        return _result;
    }

    function trade(address _sender, Order.TradeDirections _direction, IMarket _market, uint256 _outcome, uint256 _fxpAmount, uint256 _price, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId, uint256 _loopLimit) internal returns (bytes32) {
        uint256 _bestFxpAmount = fillBestOrder(_sender, _direction, _market, _outcome, _fxpAmount, _price, _tradeGroupId, _loopLimit);
        if (_bestFxpAmount == 0) {
            return bytes32(1);
        }
        return ICreateOrder(controller.lookup("CreateOrder")).createOrder(_sender, Order.getOrderTradingTypeFromMakerDirection(_direction), _bestFxpAmount, _price, _market, _outcome, _betterOrderId, _worseOrderId, _tradeGroupId);
    }

    function fillBestOrder(address _sender, Order.TradeDirections _direction, IMarket _market, uint256 _outcome, uint256 _fxpAmount, uint256 _price, bytes32 _tradeGroupId, uint256 _loopLimit) internal nonReentrant returns (uint256 _bestFxpAmount) {
        // we need to fill a BID if we want to SELL and we need to fill an ASK if we want to BUY
        Order.Types _type = Order.getOrderTradingTypeFromFillerDirection(_direction);
        IOrders _orders = IOrders(controller.lookup("Orders"));
        bytes32 _orderId = _orders.getBestOrderId(_type, _market, _outcome);
        _bestFxpAmount = _fxpAmount;
        uint256 _orderPrice = _orders.getPrice(_orderId);
        // If the price is acceptable relative to the trade type
        while (_orderId != 0 && _bestFxpAmount > 0 && _loopLimit > 0 && isMatch(_orderId, _type, _orderPrice, _price)) {
            bytes32 _nextOrderId = _orders.getWorseOrderId(_orderId);
            _orders.setPrice(_market, _outcome, _orderPrice);
            _bestFxpAmount = IFillOrder(controller.lookup("FillOrder")).fillOrder(_sender, _orderId, _bestFxpAmount, _tradeGroupId);
            _orderId = _nextOrderId;
            _orderPrice = _orders.getPrice(_orderId);
            _loopLimit -= 1;
        }
        if (_orderId != 0 && isMatch(_orderId, _type, _orderPrice, _price)) {
            return 0;
        }
        return _bestFxpAmount;
    }

    function isMatch(bytes32 _orderId, Order.Types _type, uint256 _orderPrice, uint256 _price) private returns (bool) {
        if (_orderId == 0) {
            return false;
        }
        return _type == Order.Types.Bid ? _orderPrice >= _price : _orderPrice <= _price;
    }

    function publicBuyWithAmount(IMarket _market, uint256 _outcome, uint256 _totalAmount, uint256 _price, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId, uint256 _loopLimit) external payable marketIsLegit(_market) convertToAndFromCash returns (bytes32) {
        uint256 _fxpAmount = _totalAmount / _price;
        bytes32 _result = trade(msg.sender, Order.TradeDirections.Long, _market, _outcome, _fxpAmount, _price, _betterOrderId, _worseOrderId, _tradeGroupId, _loopLimit);
        _market.assertBalances();
        return _result;
    }

    function publicSellWithAmount(IMarket _market, uint256 _outcome, uint256 _totalAmount, uint256 _price, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId, uint256 _loopLimit) external payable marketIsLegit(_market) convertToAndFromCash returns (bytes32) {
        uint256 _fxpAmount = _totalAmount / _price;
        bytes32 _result = trade(msg.sender, Order.TradeDirections.Short, _market, _outcome, _fxpAmount, _price, _betterOrderId, _worseOrderId, _tradeGroupId, _loopLimit);
        _market.assertBalances();
        return _result;
    }

    function publicTradeWithAmount(Order.TradeDirections _direction, IMarket _market, uint256 _outcome, uint256 _totalAmount, uint256 _price, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId, uint256 _loopLimit) external payable marketIsLegit(_market) convertToAndFromCash returns (bytes32) {
        uint256 _fxpAmount = _totalAmount / _price;
        bytes32 _result = trade(msg.sender, _direction, _market, _outcome, _fxpAmount, _price, _betterOrderId, _worseOrderId, _tradeGroupId, _loopLimit);
        _market.assertBalances();
        return _result;
    }

    function publicFillBestOrderWithAmount(Order.TradeDirections _direction, IMarket _market, uint256 _outcome, uint256 _totalAmount, uint256 _price, bytes32 _tradeGroupId, uint256 _loopLimit) external payable marketIsLegit(_market) convertToAndFromCash returns (uint256) {
        uint256 _fxpAmount = _totalAmount / _price;
        uint256 _result = fillBestOrder(msg.sender, _direction, _market, _outcome, _fxpAmount, _price, _tradeGroupId, _loopLimit);
        _market.assertBalances();
        return _result;
    }
}
