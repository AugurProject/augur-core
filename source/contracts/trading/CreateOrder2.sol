// Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE

pragma solidity 0.4.20;


import 'Controlled.sol';
import 'libraries/ReentrancyGuard.sol';
import 'libraries/MarketValidator.sol';
import 'trading/Order.sol';
import 'trading/ICreateOrder.sol';
import 'libraries/CashAutoConverter.sol';
import 'trading/IOrdersFetcher.sol';


contract CreateOrder2 is CashAutoConverter, ReentrancyGuard, MarketValidator {
    using Order for Order.Data;

    // CONSIDER: Do we want the API to be in terms of shares as it is now, or would the desired amount of ETH to place be preferable? Would both be useful?
    function publicCreateOrder(Order.Types _type, uint256 _attoshares, uint256 _displayPrice, IMarket _market, uint256 _outcome, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId) external payable marketIsLegit(_market) convertToAndFromCash onlyInGoodTimes returns (bytes32) {
        bytes32 _result = this.createOrder(msg.sender, _type, _attoshares, _displayPrice, _market, _outcome, _betterOrderId, _worseOrderId, _tradeGroupId);
        _market.assertBalances();
        return _result;
    }

    function createOrder(address _creator, Order.Types _type, uint256 _attoshares, uint256 _displayPrice, IMarket _market, uint256 _outcome, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId) external onlyWhitelistedCallers nonReentrant returns (bytes32) {
        IOrders _orders = IOrders(controller.lookup("Orders"));
        bytes32 _newBetterOrderId = _betterOrderId;
        _newBetterOrderId = getBetterOrderId(_type, _displayPrice, _market, _outcome, _betterOrderId, _worseOrderId);
        uint256 betterOrderPrice = _orders.getPrice(_newBetterOrderId);
        bytes32 betterOrderChildId = _orders.getWorseOrderId(_newBetterOrderId);
        while (betterOrderChildId != 0 && betterOrderPrice == _displayPrice) {
            _newBetterOrderId = betterOrderChildId;
            betterOrderChildId = _orders.getWorseOrderId(_newBetterOrderId);
            betterOrderPrice = _orders.getPrice(betterOrderChildId);
        }
        return ICreateOrder(controller.lookup("CreateOrder")).createOrder(_creator, _type, _attoshares, _displayPrice, _market, _outcome, _newBetterOrderId, _worseOrderId, _tradeGroupId);
    }

    function getBetterOrderId(Order.Types _type, uint256 _displayPrice, IMarket _market, uint256 _outcome, bytes32 _betterOrderId, bytes32 _worseOrderId) private returns (bytes32) {
        IOrders _orders = IOrders(controller.lookup("Orders"));
        bytes32 _bestOrderId = _orders.getBestOrderId(_type, _market, _outcome);
        bytes32 _worstOrderId = _orders.getWorstOrderId(_type, _market, _outcome);
        // Below is to address the bug in Orders.sol:258 and Orders.sol::280
        require(_bestOrderId != _worstOrderId || _displayPrice != _orders.getPrice(_bestOrderId));
        IOrdersFetcher _ordersFetcher = IOrdersFetcher(controller.lookup("OrdersFetcher"));
        (_betterOrderId, _worseOrderId) = _ordersFetcher.findBoundingOrders(_type, _displayPrice, _bestOrderId, _worstOrderId, _betterOrderId, _worseOrderId);
        return _betterOrderId;
    }
}
