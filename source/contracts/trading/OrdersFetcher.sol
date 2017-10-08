/**
 * Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE
 */

pragma solidity 0.4.17;
pragma experimental ABIEncoderV2;
pragma experimental "v0.5.0";

import 'trading/IOrdersFetcher.sol';
import 'Controlled.sol';
import 'libraries/arrays/Bytes32Arrays.sol';
import 'trading/Order.sol';
import 'reporting/IMarket.sol';
import 'trading/IOrders.sol';


/**
 * @title OrdersFetcher
 */
contract OrdersFetcher is Controlled, IOrdersFetcher {
    using Bytes32Arrays for bytes32[];

    function getOrder(bytes32 _orderId) public constant returns (uint256 _attoshares, uint256 _displayPrice, address _owner, uint256 _sharesEscrowed, uint256 _tokensEscrowed, bytes32 _betterOrderId, bytes32 _worseOrderId, uint256 _gasPrice) {
        IOrders _orders = IOrders(controller.lookup("Orders"));
        _attoshares = _orders.getAmount(_orderId);
        _displayPrice = _orders.getPrice(_orderId);
        _owner = _orders.getOrderCreator(_orderId);
        _tokensEscrowed = _orders.getOrderMoneyEscrowed(_orderId);
        _sharesEscrowed = _orders.getOrderSharesEscrowed(_orderId);
        _betterOrderId = _orders.getBetterOrderId(_orderId);
        _worseOrderId = _orders.getWorseOrderId(_orderId);
        return (_attoshares, _displayPrice, _owner, _tokensEscrowed, _sharesEscrowed, _betterOrderId, _worseOrderId, 0);
    }

    function ascendOrderList(Order.TradeTypes _type, uint256 _price, bytes32 _lowestOrderId) public constant returns (bytes32 _betterOrderId, bytes32 _worseOrderId) {
        _worseOrderId = _lowestOrderId;
        bool _isWorstPrice;
        IOrders _orders = IOrders(controller.lookup("Orders"));
        if (_type == Order.TradeTypes.Bid) {
            _isWorstPrice = _price <= _orders.getPrice(_worseOrderId);
        } else if (_type == Order.TradeTypes.Ask) {
            _isWorstPrice = _price >= _orders.getPrice(_worseOrderId);
        }
        if (_isWorstPrice) {
            return (_worseOrderId, _orders.getWorseOrderId(_worseOrderId));
        }
        bool _isBetterPrice = _orders.isBetterPrice(_type, _price, _worseOrderId);
        while (_isBetterPrice && _orders.getBetterOrderId(_worseOrderId) != 0 && _price != _orders.getPrice(_orders.getBetterOrderId(_worseOrderId))) {
            _betterOrderId = _orders.getBetterOrderId(_worseOrderId);
            _isBetterPrice = _orders.isBetterPrice(_type, _price, _betterOrderId);
            if (_isBetterPrice) {
                _worseOrderId = _orders.getBetterOrderId(_worseOrderId);
            }
        }
        _betterOrderId = _orders.getBetterOrderId(_worseOrderId);
        return (_betterOrderId, _worseOrderId);
    }

    function descendOrderList(Order.TradeTypes _type, uint256 _price, bytes32 _highestOrderId) public constant returns (bytes32 _betterOrderId, bytes32 _worseOrderId) {
        _betterOrderId = _highestOrderId;
        bool _isBestPrice;
        IOrders _orders = IOrders(controller.lookup("Orders"));
        if (_type == Order.TradeTypes.Bid) {
            _isBestPrice = _price > _orders.getPrice(_betterOrderId);
        } else if (_type == Order.TradeTypes.Ask) {
            _isBestPrice = _price < _orders.getPrice(_betterOrderId);
        }
        if (_isBestPrice) {
            return (0, _betterOrderId);
        }
        if (_price == _orders.getPrice(_betterOrderId)) {
            return (_betterOrderId, _orders.getWorseOrderId(_betterOrderId));
        }
        bool _isWorsePrice = _orders.isWorsePrice(_type, _price, _betterOrderId);
        while (_isWorsePrice && _orders.getWorseOrderId(_betterOrderId) != 0) {
            _worseOrderId = _orders.getWorseOrderId(_betterOrderId);
            _isWorsePrice = _orders.isWorsePrice(_type, _price, _worseOrderId);
            if (_isWorsePrice || _price == _orders.getPrice(_orders.getWorseOrderId(_betterOrderId))) {
                _betterOrderId = _orders.getWorseOrderId(_betterOrderId);
            }
        }
        _worseOrderId = _orders.getWorseOrderId(_betterOrderId);
        return (_betterOrderId, _worseOrderId);
    }

    function findBoundingOrders(Order.TradeTypes _type, uint256 _price, bytes32 _bestOrderId, bytes32 _worstOrderId, bytes32 _betterOrderId, bytes32 _worseOrderId) public returns (bytes32, bytes32) {
        IOrders _orders = IOrders(controller.lookup("Orders"));
        if (_bestOrderId == _worstOrderId) {
            if (_bestOrderId == bytes32(0)) {
                return (bytes32(0), bytes32(0));
            } else if (_orders.isBetterPrice(_type, _price, _bestOrderId)) {
                return (bytes32(0), _bestOrderId);
            } else {
                return (_bestOrderId, bytes32(0));
            }
        }
        if (_betterOrderId != bytes32(0)) {
            if (_orders.getPrice(_betterOrderId) == 0) {
                _betterOrderId = bytes32(0);
            } else {
                _orders.assertIsNotBetterPrice(_type, _price, _betterOrderId);
            }
        }
        if (_worseOrderId != bytes32(0)) {
            if (_orders.getPrice(_worseOrderId) == 0) {
                _worseOrderId = bytes32(0);
            } else {
                _orders.assertIsNotWorsePrice(_type, _price, _worseOrderId);
            }
        }
        if (_betterOrderId == bytes32(0) && _worseOrderId == bytes32(0)) {
            return (descendOrderList(_type, _price, _bestOrderId));
        } else if (_betterOrderId == bytes32(0)) {
            return (ascendOrderList(_type, _price, _worseOrderId));
        } else if (_worseOrderId == bytes32(0)) {
            return (descendOrderList(_type, _price, _betterOrderId));
        }
        if (_orders.getWorseOrderId(_betterOrderId) != _worseOrderId) {
            return (descendOrderList(_type, _price, _betterOrderId));
        } else if (_orders.getBetterOrderId(_worseOrderId) != _betterOrderId) {
            return (ascendOrderList(_type, _price, _worseOrderId));
        }
        return (_betterOrderId, _worseOrderId);
    }
}
