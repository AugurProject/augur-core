// Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE

pragma solidity 0.4.24;


import 'Controlled.sol';
import 'libraries/ReentrancyGuard.sol';
import 'libraries/MarketValidator.sol';
import 'trading/Order.sol';
import 'trading/ICreateOrder.sol';
import 'libraries/CashAutoConverter.sol';


contract CreateOrder is CashAutoConverter, ReentrancyGuard, MarketValidator {
    using Order for Order.Data;

    function publicCreateOrder(Order.Types _type, uint256 _attoshares, uint256 _price, IMarket _market, uint256 _outcome, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId, bool _ignoreShares) external payable marketIsLegit(_market) convertToAndFromCash returns (bytes32) {
        bytes32 _result = this.createOrder(msg.sender, _type, _attoshares, _price, _market, _outcome, _betterOrderId, _worseOrderId, _tradeGroupId, _ignoreShares);
        _market.assertBalances();
        return _result;
    }

    function createOrder(address _creator, Order.Types _type, uint256 _attoshares, uint256 _price, IMarket _market, uint256 _outcome, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId, bool _ignoreShares) external onlyWhitelistedCallers nonReentrant returns (bytes32) {
        Order.Data memory _orderData = Order.create(controller, _creator, _outcome, _type, _attoshares, _price, _market, _betterOrderId, _worseOrderId, _ignoreShares);
        Order.escrowFunds(_orderData);
        require(_orderData.orders.getAmount(_orderData.getOrderId()) == 0);
        return Order.saveOrder(_orderData, _tradeGroupId);
    }
}
