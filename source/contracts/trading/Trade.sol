// Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE

pragma solidity 0.4.20;


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
    uint256 internal constant FILL_ORDER_MINIMUM_GAS_NEEDED = 2000000;
    uint256 internal constant CREATE_ORDER_MINIMUM_GAS_NEEDED = 700000;

    function publicBuy(IMarket _market, uint256 _outcome, uint256 _fxpAmount, uint256 _price, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId) external payable marketIsLegit(_market) convertToAndFromCash onlyInGoodTimes returns (bytes32) {
        bytes32 _result = trade(msg.sender, Order.TradeDirections.Long, _market, _outcome, _fxpAmount, _price, _betterOrderId, _worseOrderId, _tradeGroupId);
        _market.assertBalances();
        return _result;
    }

    function publicSell(IMarket _market, uint256 _outcome, uint256 _fxpAmount, uint256 _price, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId) external payable marketIsLegit(_market) convertToAndFromCash onlyInGoodTimes returns (bytes32) {
        bytes32 _result = trade(msg.sender, Order.TradeDirections.Short, _market, _outcome, _fxpAmount, _price, _betterOrderId, _worseOrderId, _tradeGroupId);
        _market.assertBalances();
        return _result;
    }

    function publicTrade(Order.TradeDirections _direction, IMarket _market, uint256 _outcome, uint256 _fxpAmount, uint256 _price, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId) external payable marketIsLegit(_market) convertToAndFromCash onlyInGoodTimes returns (bytes32) {
        bytes32 _result = trade(msg.sender, _direction, _market, _outcome, _fxpAmount, _price, _betterOrderId, _worseOrderId, _tradeGroupId);
        _market.assertBalances();
        return _result;
    }

    function publicFillBestOrder(Order.TradeDirections _direction, IMarket _market, uint256 _outcome, uint256 _fxpAmount, uint256 _price, bytes32 _tradeGroupId) external payable marketIsLegit(_market) convertToAndFromCash onlyInGoodTimes returns (uint256) {
        uint256 _result = fillBestOrder(msg.sender, _direction, _market, _outcome, _fxpAmount, _price, _tradeGroupId);
        _market.assertBalances();
        return _result;
    }

    function trade(address _sender, Order.TradeDirections _direction, IMarket _market, uint256 _outcome, uint256 _fxpAmount, uint256 _price, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId) internal returns (bytes32) {
        uint256 _bestFxpAmount = fillBestOrder(_sender, _direction, _market, _outcome, _fxpAmount, _price, _tradeGroupId);
        if (_bestFxpAmount == 0) {
            return bytes32(1);
        }
        if (msg.gas < getCreateOrderMinGasNeeded()) {
            return bytes32(1);
        }
        Order.Types _type = Order.getOrderTradingTypeFromMakerDirection(_direction);
        return ICreateOrder(controller.lookup("CreateOrder")).createOrder(_sender, _type, _bestFxpAmount, _price, _market, _outcome, _betterOrderId, _worseOrderId, _tradeGroupId);
    }

    function fillBestOrder(address _sender, Order.TradeDirections _direction, IMarket _market, uint256 _outcome, uint256 _fxpAmount, uint256 _price, bytes32 _tradeGroupId) internal nonReentrant returns (uint256 _bestFxpAmount) {
        // we need to fill a BID if we want to SELL and we need to fill an ASK if we want to BUY
        Order.Types _type = Order.getOrderTradingTypeFromFillerDirection(_direction);
        IOrders _orders = IOrders(controller.lookup("Orders"));
        bytes32 _orderId = _orders.getBestOrderId(_type, _market, _outcome);
        _bestFxpAmount = _fxpAmount;

        while (_orderId != 0 && _bestFxpAmount > 0 && msg.gas >= getFillOrderMinGasNeeded()) {
            uint256 _orderPrice = _orders.getPrice(_orderId);
            // If the price is acceptable relative to the trade type
            if (_type == Order.Types.Bid ? _orderPrice >= _price : _orderPrice <= _price) {
                bytes32 _nextOrderId = _orders.getWorseOrderId(_orderId);
                _orders.setPrice(_market, _outcome, _orderPrice);
                _bestFxpAmount = IFillOrder(controller.lookup("FillOrder")).fillOrder(_sender, _orderId, _bestFxpAmount, _tradeGroupId);
                _orderId = _nextOrderId;
            } else {
                _orderId = bytes32(0);
            }
        }
        if (_orderId != 0) {
            return 0;
        }
        return _bestFxpAmount;
    }

    function publicBuyWithLimit(IMarket _market, uint256 _outcome, uint256 _fxpAmount, uint256 _price, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId, uint256 _loopLimit) external payable marketIsLegit(_market) convertToAndFromCash onlyInGoodTimes returns (bytes32) {
        bytes32 _result = tradeWithLimit(msg.sender, Order.TradeDirections.Long, _market, _outcome, _fxpAmount, _price, _betterOrderId, _worseOrderId, _tradeGroupId, _loopLimit);
        _market.assertBalances();
        return _result;
    }

    function publicSellWithLimit(IMarket _market, uint256 _outcome, uint256 _fxpAmount, uint256 _price, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId, uint256 _loopLimit) external payable marketIsLegit(_market) convertToAndFromCash onlyInGoodTimes returns (bytes32) {
        bytes32 _result = tradeWithLimit(msg.sender, Order.TradeDirections.Short, _market, _outcome, _fxpAmount, _price, _betterOrderId, _worseOrderId, _tradeGroupId, _loopLimit);
        _market.assertBalances();
        return _result;
    }

    function publicTradeWithLimit(Order.TradeDirections _direction, IMarket _market, uint256 _outcome, uint256 _fxpAmount, uint256 _price, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId, uint256 _loopLimit) external payable marketIsLegit(_market) convertToAndFromCash onlyInGoodTimes returns (bytes32) {
        bytes32 _result = tradeWithLimit(msg.sender, _direction, _market, _outcome, _fxpAmount, _price, _betterOrderId, _worseOrderId, _tradeGroupId, _loopLimit);
        _market.assertBalances();
        return _result;
    }

    function publicFillBestOrderWithLimit(Order.TradeDirections _direction, IMarket _market, uint256 _outcome, uint256 _fxpAmount, uint256 _price, bytes32 _tradeGroupId, uint256 _loopLimit) external payable marketIsLegit(_market) convertToAndFromCash onlyInGoodTimes returns (uint256) {
        uint256 _result = fillBestOrderWithLimit(msg.sender, _direction, _market, _outcome, _fxpAmount, _price, _tradeGroupId, _loopLimit);
        _market.assertBalances();
        return _result;
    }

    function tradeWithLimit(address _sender, Order.TradeDirections _direction, IMarket _market, uint256 _outcome, uint256 _fxpAmount, uint256 _price, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId, uint256 _loopLimit) internal returns (bytes32) {
        uint256 _bestFxpAmount = fillBestOrderWithLimit(_sender, _direction, _market, _outcome, _fxpAmount, _price, _tradeGroupId, _loopLimit);
        if (_bestFxpAmount == 0) {
            return bytes32(1);
        }
        return ICreateOrder(controller.lookup("CreateOrder")).createOrder(_sender, Order.getOrderTradingTypeFromMakerDirection(_direction), _bestFxpAmount, _price, _market, _outcome, _betterOrderId, _worseOrderId, _tradeGroupId);
    }

    function fillBestOrderWithLimit(address _sender, Order.TradeDirections _direction, IMarket _market, uint256 _outcome, uint256 _fxpAmount, uint256 _price, bytes32 _tradeGroupId, uint256 _loopLimit) internal nonReentrant returns (uint256 _bestFxpAmount) {
        // we need to fill a BID if we want to SELL and we need to fill an ASK if we want to BUY
        Order.Types _type = Order.getOrderTradingTypeFromFillerDirection(_direction);
        IOrders _orders = IOrders(controller.lookup("Orders"));
        bytes32 _orderId = _orders.getBestOrderId(_type, _market, _outcome);
        _bestFxpAmount = _fxpAmount;
        while (_orderId != 0 && _bestFxpAmount > 0 && _loopLimit > 0) {
            uint256 _orderPrice = _orders.getPrice(_orderId);
            // If the price is acceptable relative to the trade type
            if (_type == Order.Types.Bid ? _orderPrice >= _price : _orderPrice <= _price) {
                bytes32 _nextOrderId = _orders.getWorseOrderId(_orderId);
                if (_orders.getOrderCreator(_orderId) != _sender) {
                    _orders.setPrice(_market, _outcome, _orderPrice);
                    _bestFxpAmount = IFillOrder(controller.lookup("FillOrder")).fillOrder(_sender, _orderId, _bestFxpAmount, _tradeGroupId);
                }
                _orderId = _nextOrderId;
            } else {
                _orderId = bytes32(0);
            }
            _loopLimit -= 1;
        }
        if (_orderId != 0) {
            return 0;
        }
        return _bestFxpAmount;
    }

    // COVERAGE: This is not covered and cannot be. We need to use a different minimum gas while running coverage since the additional logging make the cost rise a great deal
    function getFillOrderMinGasNeeded() internal pure returns (uint256) {
        return FILL_ORDER_MINIMUM_GAS_NEEDED;
    }

    function getCreateOrderMinGasNeeded() internal pure returns (uint256) {
        return CREATE_ORDER_MINIMUM_GAS_NEEDED;
    }
}
