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

    struct Data {
        Order.TradeDirections direction;
        IMarket market;
        uint256 outcome;
        uint256 amount;
        uint256 price;
        bytes32 betterOrderId;
        bytes32 worseOrderId;
        bytes32 tradeGroupId;
        uint256 loopLimit;
        bool ignoreShares;
        address sender;
    }

    function create(Order.TradeDirections _direction, IMarket _market, uint256 _outcome, uint256 _amount, uint256 _price, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId, uint256 _loopLimit, bool _ignoreShares, address _sender) internal pure returns (Data) {
        require(_amount > 0);

        return Data({
            direction: _direction,
            market: _market,
            outcome: _outcome,
            amount: _amount,
            price: _price,
            betterOrderId: _betterOrderId,
            worseOrderId: _worseOrderId,
            tradeGroupId: _tradeGroupId,
            loopLimit: _loopLimit,
            ignoreShares: _ignoreShares,
            sender: _sender
        });
    }

    function createWithTotalCost(Order.TradeDirections _direction, IMarket _market, uint256 _outcome, uint256 _totalCost, uint256 _price, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId, uint256 _loopLimit, bool _ignoreShares, address _sender) internal pure returns (Data) {
        return create(_direction, _market, _outcome, _totalCost / _price, _price, _betterOrderId, _worseOrderId, _tradeGroupId, _loopLimit, _ignoreShares, _sender);
    }

    function publicTrade(Order.TradeDirections _direction, IMarket _market, uint256 _outcome, uint256 _amount, uint256 _price, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId, uint256 _loopLimit, bool _ignoreShares) external payable marketIsLegit(_market) convertToAndFromCash returns (bytes32) {
        Data memory _tradeData = create(_direction, _market, _outcome, _amount, _price, _betterOrderId, _worseOrderId, _tradeGroupId, _loopLimit, _ignoreShares, msg.sender);
        bytes32 _result = trade(_tradeData);
        _market.assertBalances();
        return _result;
    }

    function publicFillBestOrder(Order.TradeDirections _direction, IMarket _market, uint256 _outcome, uint256 _amount, uint256 _price, bytes32 _tradeGroupId, uint256 _loopLimit, bool _ignoreShares) external payable marketIsLegit(_market) convertToAndFromCash returns (uint256) {
        Data memory _tradeData = create(_direction, _market, _outcome, _amount, _price, bytes32(0), bytes32(0), _tradeGroupId, _loopLimit, _ignoreShares, msg.sender);
        uint256 _result = fillBestOrder(_tradeData);
        _market.assertBalances();
        return _result;
    }

    function trade(Data _tradeData) internal returns (bytes32) {
        uint256 _bestAmount = fillBestOrder(_tradeData);
        if (_bestAmount == 0) {
            return bytes32(1);
        }
        return ICreateOrder(controller.lookup("CreateOrder")).createOrder(_tradeData.sender, Order.getOrderTradingTypeFromMakerDirection(_tradeData.direction), _bestAmount, _tradeData.price, _tradeData.market, _tradeData.outcome, _tradeData.betterOrderId, _tradeData.worseOrderId, _tradeData.tradeGroupId, _tradeData.ignoreShares);
    }

    function fillBestOrder(Data _tradeData) internal nonReentrant returns (uint256 _bestAmount) {
        // we need to fill a BID if we want to SELL and we need to fill an ASK if we want to BUY
        Order.Types _type = Order.getOrderTradingTypeFromFillerDirection(_tradeData.direction);
        IOrders _orders = IOrders(controller.lookup("Orders"));
        bytes32 _orderId = _orders.getBestOrderId(_type, _tradeData.market, _tradeData.outcome);
        _bestAmount = _tradeData.amount;
        uint256 _orderPrice = _orders.getPrice(_orderId);
        // If the price is acceptable relative to the trade type
        while (_orderId != 0 && _bestAmount > 0 && _tradeData.loopLimit > 0 && isMatch(_orderId, _type, _orderPrice, _tradeData.price)) {
            bytes32 _nextOrderId = _orders.getWorseOrderId(_orderId);
            _orders.setPrice(_tradeData.market, _tradeData.outcome, _orderPrice);
            _bestAmount = IFillOrder(controller.lookup("FillOrder")).fillOrder(_tradeData.sender, _orderId, _bestAmount, _tradeData.tradeGroupId, _tradeData.ignoreShares);
            _orderId = _nextOrderId;
            _orderPrice = _orders.getPrice(_orderId);
            _tradeData.loopLimit -= 1;
        }
        if (isMatch(_orderId, _type, _orderPrice, _tradeData.price)) {
            return 0;
        }
        return _bestAmount;
    }

    function isMatch(bytes32 _orderId, Order.Types _type, uint256 _orderPrice, uint256 _price) private pure returns (bool) {
        if (_orderId == 0) {
            return false;
        }
        return _type == Order.Types.Bid ? _orderPrice >= _price : _orderPrice <= _price;
    }

    function publicTradeWithTotalCost(Order.TradeDirections _direction, IMarket _market, uint256 _outcome, uint256 _totalCost, uint256 _price, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId, uint256 _loopLimit, bool _ignoreShares) external payable marketIsLegit(_market) convertToAndFromCash returns (bytes32) {
        Data memory _tradeData = createWithTotalCost(_direction, _market, _outcome, _totalCost, _price, _betterOrderId, _worseOrderId, _tradeGroupId, _loopLimit, _ignoreShares, msg.sender);
        bytes32 _result = trade(_tradeData);
        _market.assertBalances();
        return _result;
    }

    function publicFillBestOrderWithTotalCost(Order.TradeDirections _direction, IMarket _market, uint256 _outcome, uint256 _totalCost, uint256 _price, bytes32 _tradeGroupId, uint256 _loopLimit, bool _ignoreShares) external payable marketIsLegit(_market) convertToAndFromCash returns (uint256) {
        Data memory _tradeData = createWithTotalCost(_direction, _market, _outcome, _totalCost, _price, bytes32(0), bytes32(0), _tradeGroupId, _loopLimit, _ignoreShares, msg.sender);
        uint256 _result = fillBestOrder(_tradeData);
        _market.assertBalances();
        return _result;
    }
}
