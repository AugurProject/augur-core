// Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE

pragma solidity 0.4.18;


import 'Controlled.sol';
import 'libraries/ReentrancyGuard.sol';
import 'trading/Order.sol';
import 'trading/ICreateOrder.sol';
import 'libraries/CashAutoConverter.sol';
import 'libraries/Extractable.sol';


contract CreateOrder is CashAutoConverter, Extractable, ReentrancyGuard {
    using Order for Order.Data;

    // CONSIDER: Do we want the API to be in terms of shares as it is now, or would the desired amount of ETH to place be preferable? Would both be useful?
    function publicCreateOrder(Order.Types _type, uint256 _attoshares, uint256 _displayPrice, IMarket _market, uint8 _outcome, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId) external payable convertToAndFromCash onlyInGoodTimes nonReentrant returns (bytes32) {
        return this.createOrder(msg.sender, _type, _attoshares, _displayPrice, _market, _outcome, _betterOrderId, _worseOrderId, _tradeGroupId);
    }

    function createOrder(address _creator, Order.Types _type, uint256 _attoshares, uint256 _displayPrice, IMarket _market, uint8 _outcome, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId) external onlyWhitelistedCallers returns (bytes32) {
        Order.Data memory _orderData = Order.create(controller, _creator, _outcome, _type, _attoshares, _displayPrice, _market, _betterOrderId, _worseOrderId);
        Order.escrowFunds(_orderData);
        require(_orderData.orders.getAmount(_orderData.getOrderId()) == 0);
        return Order.saveOrder(_orderData, _tradeGroupId);
    }

    function getProtectedTokens() internal returns (address[] memory) {
        return new address[](0);
    }
}
