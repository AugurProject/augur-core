/**
 * Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE
 */

pragma solidity ^0.4.13;

import 'ROOT/Controller.sol';
import 'ROOT/libraries/arrays/Bytes20Arrays.sol';
import 'ROOT/reporting/Interfaces.sol';
import 'ROOT/trading/NewOrders.sol';


/**
 * @title OrdersFetcher
 */
contract NewOrdersFetcher is Controlled {
    using Bytes20Arrays for bytes20[];

    event Log(uint256 fxpPrice);

    // Trade types
    uint8 private constant BID = 1;
    uint8 private constant ASK = 2;
    
    /**
     * @dev Get orders for a particular market, type, and outcome (chunked)
     */
    function getOrderIds(uint256 _type, IMarket _market, uint8 _outcome, bytes20 _startingOrderId, uint256 _numOrdersToLoad) public constant returns (bytes20[]) {
        require(_type == BID || _type == ASK);
        require(0 <= _outcome && _outcome < _market.getNumberOfOutcomes());
        var _orders = NewOrders(controller.lookup("NewOrders"));
        if (_startingOrderId == 0) {
            _startingOrderId = _orders.getBestOrderId(_type, _market, _outcome);
        }
        bytes20[] _orderIds;
        _orderIds[0] = _startingOrderId;
        uint256 _i = 0;
        while (_i < _numOrdersToLoad && _orders.getWorseOrderId(_orderIds[_i], _type, _market, _outcome) != 0) {
            _orderIds[_i + 1] = _orders.getWorseOrderId(_orderIds[_i], _type, _market, _outcome);
            _i += 1;
        }
        return (_orderIds.slice(0, _i));
    }

    function getOrder(bytes20 _orderId, uint256 _type, IMarket _market, uint8 _outcome) public constant returns (uint256 _attoshares, uint256 _displayPrice, address _owner, uint256 _tokensEscrowed, uint256 _sharesEscrowed, bytes20 _betterOrderId, bytes20 _worseOrderId, uint256 _gasPrice) {
        var _orders = NewOrders(controller.lookup("NewOrders"));
        _attoshares = _orders.getAmount(_orderId, _type, _market, _outcome);
        _displayPrice = _orders.getPrice(_orderId, _type, _market, _outcome);
        _owner = _orders.getOrderOwner(_orderId, _type, _market, _outcome);
        _tokensEscrowed = _orders.getOrderMoneyEscrowed(_orderId, _type, _market, _outcome);
        _sharesEscrowed = _orders.getOrderSharesEscrowed(_orderId, _type, _market, _outcome);
        _betterOrderId = _orders.getBetterOrderId(_orderId, _type, _market, _outcome);
        _worseOrderId = _orders.getWorseOrderId(_orderId, _type, _market, _outcome);
        _gasPrice = _orders.getGasPrice(_orderId, _type, _market, _outcome);
        return (_attoshares, _displayPrice, _owner, _tokensEscrowed, _sharesEscrowed, _betterOrderId, _worseOrderId, _gasPrice);
    }

    function ascendOrderList(uint256 _type, IMarket _market, uint8 _outcome, uint256 _fxpPrice, bytes20 _lowestOrderId) public constant returns (bytes20 _betterOrderId, bytes20 _worseOrderId) {
        _worseOrderId = _lowestOrderId;
        bool _isWorstPrice;
        var _orders = NewOrders(controller.lookup("NewOrders"));
        if (_type == BID) {
            _isWorstPrice = _fxpPrice <= _orders.getPrice(_worseOrderId, _type, _market, _outcome);
        } else {
            _isWorstPrice = _fxpPrice >= _orders.getPrice(_worseOrderId, _type, _market, _outcome);
        }
        if (_isWorstPrice) {
            return (_worseOrderId, _orders.getWorseOrderId(_worseOrderId, _type, _market, _outcome));
        }
        bool _isBetterPrice = _orders.isBetterPrice(_type, _market, _outcome, _fxpPrice, _worseOrderId);
        while (_isBetterPrice && _orders.getBetterOrderId(_worseOrderId, _type, _market, _outcome) != 0 && _fxpPrice != _orders.getPrice(_orders.getBetterOrderId(_worseOrderId, _type, _market, _outcome), _type, _market, _outcome)) {
            _betterOrderId = _orders.getBetterOrderId(_worseOrderId, _type, _market, _outcome);
            _isBetterPrice = _orders.isBetterPrice(_type, _market, _outcome, _fxpPrice, _betterOrderId);
            if (_isBetterPrice) {
                _worseOrderId = _orders.getBetterOrderId(_worseOrderId, _type, _market, _outcome);
            }
        }
        _betterOrderId = _orders.getBetterOrderId(_worseOrderId, _type, _market, _outcome);
        return (_betterOrderId, _worseOrderId);
    }

    function descendOrderList(uint256 _type, IMarket _market, uint8 _outcome, uint256 _fxpPrice, bytes20 _highestOrderId) public constant returns (bytes20 _betterOrderId, bytes20 _worseOrderId) {
        _betterOrderId = _highestOrderId;
        bool _isBestPrice;
        var _orders = NewOrders(controller.lookup("NewOrders"));
        if (_type == BID) {
            _isBestPrice = _fxpPrice > _orders.getPrice(_betterOrderId, _type, _market, _outcome);
        } else {
            _isBestPrice = _fxpPrice < _orders.getPrice(_betterOrderId, _type, _market, _outcome);
        }
        if (_isBestPrice) {
            return (0, _betterOrderId);
        }
        if (_fxpPrice == _orders.getPrice(_betterOrderId, _type, _market, _outcome)) {
            return (_betterOrderId, _orders.getWorseOrderId(_betterOrderId, _type, _market, _outcome));
        }
        bool _isWorsePrice = _orders.isWorsePrice(_type, _market, _outcome, _fxpPrice, _betterOrderId);
        while (_isWorsePrice && _orders.getWorseOrderId(_betterOrderId, _type, _market, _outcome) != 0) {
            _worseOrderId = _orders.getWorseOrderId(_betterOrderId, _type, _market, _outcome);
            _isWorsePrice = _orders.isWorsePrice(_type, _market, _outcome, _fxpPrice, _worseOrderId);
            if (_isWorsePrice || _fxpPrice == _orders.getPrice(_orders.getWorseOrderId(_betterOrderId, _type, _market, _outcome), _type, _market, _outcome)) {
                _betterOrderId = _orders.getWorseOrderId(_betterOrderId, _type, _market, _outcome);
            }
        }
        _worseOrderId = _orders.getWorseOrderId(_betterOrderId, _type, _market, _outcome);
        return (_betterOrderId, _worseOrderId);
    }

    function findBoundingOrders(uint256 _type, IMarket _market, uint8 _outcome, uint256 _fxpPrice, bytes20 _bestOrderId, bytes20 _worstOrderId, bytes20 _betterOrderId, bytes20 _worseOrderId) public constant returns (bytes20, bytes20) {
        var _orders = NewOrders(controller.lookup("NewOrders"));
        if (_bestOrderId == _worstOrderId) {
            if (_bestOrderId == 0) {
                return (0, 0);
            } else if (_orders.isBetterPrice(_type, _market, _outcome, _fxpPrice, _bestOrderId)) {
                return (0, _bestOrderId);
            } else {
                return (_bestOrderId, 0);
            }
        }
        if (_betterOrderId != 0) {
            if (_orders.getPrice(_betterOrderId, _type, _market, _outcome) == 0) {
                _betterOrderId = 0;
            } else {
                _orders.assertIsNotBetterPrice(_type, _market, _outcome, _fxpPrice, _betterOrderId);
            }
        }
        if (_worseOrderId != 0) {
            if (_orders.getPrice(_worseOrderId, _type, _market, _outcome) == 0) {
                _worseOrderId = 0;
            } else {
                _orders.assertIsNotWorsePrice(_type, _market, _outcome, _fxpPrice, _worseOrderId);
            }
        }
        if (_betterOrderId == 0 && _worseOrderId == 0) {
            return (descendOrderList(_type, _market, _outcome, _fxpPrice, _bestOrderId));
        } else if (_betterOrderId == 0) {
            return (ascendOrderList(_type, _market, _outcome, _fxpPrice, _worseOrderId));
        } else if (_worseOrderId == 0) {
            return (descendOrderList(_type, _market, _outcome, _fxpPrice, _betterOrderId));
        }
        if (_orders.getWorseOrderId(_betterOrderId, _type, _market, _outcome) != _worseOrderId) {
            return (descendOrderList(_type, _market, _outcome, _fxpPrice, _betterOrderId));
        } else if (_orders.getBetterOrderId(_worseOrderId, _type, _market, _outcome) != _betterOrderId) {
            return (ascendOrderList(_type, _market, _outcome, _fxpPrice, _worseOrderId));
        }
        return (_betterOrderId, _worseOrderId);
    }
}
