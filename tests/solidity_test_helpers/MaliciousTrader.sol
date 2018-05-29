pragma solidity 0.4.20;

import 'trading/ICash.sol';
import 'trading/Order.sol';
import 'trading/ICreateOrder.sol';


contract MaliciousTrader {
    bool evil = false;

    function approveAugur(ICash _cash, address _augur) public returns (bool) {
        _cash.approve(_augur, 2**254);
        return true;
    }

    function makeOrder(ICreateOrder _createOrder, Order.Types _type, uint256 _attoshares, uint256 _displayPrice, IMarket _market, uint256 _outcome, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId) external payable returns (bytes32) {
        return _createOrder.publicCreateOrder.value(msg.value)(_type, _attoshares, _displayPrice, _market, _outcome, _betterOrderId, _worseOrderId, _tradeGroupId);
    }

    function setEvil(bool _evil) public returns (bool) {
        evil = _evil;
    }

    function () payable {
        if (evil) {
            revert();
        }
    }
}