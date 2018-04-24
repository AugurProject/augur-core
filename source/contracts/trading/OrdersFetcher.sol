/**
 * Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE
 */

pragma solidity 0.4.20;


import 'trading/IOrdersFetcher.sol';
import 'Controlled.sol';
import 'trading/Order.sol';
import 'reporting/IMarket.sol';
import 'trading/IOrders.sol';


/**
 * @title OrdersFetcher
 */
contract OrdersFetcher is Controlled, IOrdersFetcher {
    function ascendOrderList(Order.Types _type, uint256 _price, bytes32 _lowestOrderId) public view returns (bytes32 _betterOrderId, bytes32 _worseOrderId) {
        _worseOrderId = _lowestOrderId;
        bool _isWorstPrice;
        IOrders _orders = IOrders(controller.lookup("Orders"));
        if (_type == Order.Types.Bid) {
            _isWorstPrice = _price <= _orders.getPrice(_worseOrderId);
        } else if (_type == Order.Types.Ask) {
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

    function descendOrderList(Order.Types _type, uint256 _price, bytes32 _highestOrderId) public view returns (bytes32 _betterOrderId, bytes32 _worseOrderId) {
        _betterOrderId = _highestOrderId;
        bool _isBestPrice;
        IOrders _orders = IOrders(controller.lookup("Orders"));
        if (_type == Order.Types.Bid) {
            _isBestPrice = _price > _orders.getPrice(_betterOrderId);
        } else if (_type == Order.Types.Ask) {
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

    function findBoundingOrders(Order.Types _type, uint256 _price, bytes32 _bestOrderId, bytes32 _worstOrderId, bytes32 _betterOrderId, bytes32 _worseOrderId) public returns (bytes32, bytes32) {
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
            // Coverage: This condition is likely unreachable or at least seems to be. Rather than remove it I'm keeping it for now just to be paranoid
            return (ascendOrderList(_type, _price, _worseOrderId));
        }
        return (_betterOrderId, _worseOrderId);
    }
}
