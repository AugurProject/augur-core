/**
 * Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE
 */

pragma solidity ^0.4.13;

import 'ROOT/Controller.sol';
import 'ROOT/libraries/arrays/Bytes32Arrays.sol';
import 'ROOT/libraries/Trading.sol';
import 'ROOT/reporting/Interfaces.sol';
import 'ROOT/trading/Orders.sol';


/**
 * @title OrdersFetcher
 */
contract OrdersFetcher is Controlled {
    using Bytes32Arrays for bytes32[];

    /**
     * @dev Get orders for a particular market, type, and outcome (chunked)
     */
    function getOrderIds(Trading.TradeTypes _type, Market _market, uint8 _outcome, bytes32 _startingOrderId, uint256 _numOrdersToLoad) external constant returns (bytes32[]) {
        require(_type == Trading.TradeTypes.Bid || _type == Trading.TradeTypes.Ask);
        require(_outcome < _market.getNumberOfOutcomes());
        Orders _orders = Orders(controller.lookup("Orders"));
        bytes32[] _orderIds;
        if (_startingOrderId == bytes32(0)) {
            _orderIds[0] = _orders.getBestOrderId(_type, _market, _outcome);
        } else {
            _orderIds[0] = _startingOrderId;
        }
        for (uint256 _i = 0; _i < _numOrdersToLoad; _i++) {
            if (_orders.getWorseOrderId(_orderIds[_i], _type, _market, _outcome) != 0) {
                break;
            }
            _orderIds[_i + 1] = _orders.getWorseOrderId(_orderIds[_i], _type, _market, _outcome);
        }
        return (_orderIds.slice(0, _i));
    }

    function getOrder(bytes32 _orderId, Trading.TradeTypes _type, Market _market, uint8 _outcome) public constant returns (uint256 _attoshares, int256 _displayPrice, address _owner, uint256 _tokensEscrowed, uint256 _sharesEscrowed, bytes32 _betterOrderId, bytes32 _worseOrderId, uint256 _gasPrice) {
        Orders _orders = Orders(controller.lookup("Orders"));
        _attoshares = _orders.getAmount(_orderId, _type, _market, _outcome);
        _displayPrice = _orders.getPrice(_orderId, _type, _market, _outcome);
        _owner = _orders.getOrderOwner(_orderId, _type, _market, _outcome);
        _tokensEscrowed = _orders.getOrderMoneyEscrowed(_orderId, _type, _market, _outcome);
        _sharesEscrowed = _orders.getOrderSharesEscrowed(_orderId, _type, _market, _outcome);
        _betterOrderId = _orders.getBetterOrderId(_orderId, _type, _market, _outcome);
        _worseOrderId = _orders.getWorseOrderId(_orderId, _type, _market, _outcome);
        _gasPrice = tx.gasprice; // Gas price has been deprecated from Orders, so just set it to tx.gasprice
        return (_attoshares, _displayPrice, _owner, _tokensEscrowed, _sharesEscrowed, _betterOrderId, _worseOrderId, _gasPrice);
    }

    function ascendOrderList(Trading.TradeTypes _type, Market _market, uint8 _outcome, int256 _fxpPrice, bytes32 _lowestOrderId) public constant returns (bytes32 _betterOrderId, bytes32 _worseOrderId) {
        _worseOrderId = _lowestOrderId;
        bool _isWorstPrice;
        Orders _orders = Orders(controller.lookup("Orders"));
        if (_type == Trading.TradeTypes.Bid) {
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

    function descendOrderList(Trading.TradeTypes _type, Market _market, uint8 _outcome, int256 _fxpPrice, bytes32 _highestOrderId) public constant returns (bytes32 _betterOrderId, bytes32 _worseOrderId) {
        _betterOrderId = _highestOrderId;
        bool _isBestPrice;
        Orders _orders = Orders(controller.lookup("Orders"));
        if (_type == Trading.TradeTypes.Bid) {
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

    function findBoundingOrders(Trading.TradeTypes _type, Market _market, uint8 _outcome, int256 _fxpPrice, bytes32 _bestOrderId, bytes32 _worstOrderId, bytes32 _betterOrderId, bytes32 _worseOrderId) public constant returns (bytes32, bytes32) {
        Orders _orders = Orders(controller.lookup("Orders"));
        if (_bestOrderId == _worstOrderId) {
            if (_bestOrderId == bytes32(0)) {
                return (bytes32(0), bytes32(0));
            } else if (_orders.isBetterPrice(_type, _market, _outcome, _fxpPrice, _bestOrderId)) {
                return (bytes32(0), _bestOrderId);
            } else {
                return (_bestOrderId, bytes32(0));
            }
        }
        if (_betterOrderId != bytes32(0)) {
            if (_orders.getPrice(_betterOrderId, _type, _market, _outcome) == 0) {
                _betterOrderId = bytes32(0);
            } else {
                _orders.assertIsNotBetterPrice(_type, _market, _outcome, _fxpPrice, _betterOrderId);
            }
        }
        if (_worseOrderId != bytes32(0)) {
            if (_orders.getPrice(_worseOrderId, _type, _market, _outcome) == 0) {
                _worseOrderId = bytes32(0);
            } else {
                _orders.assertIsNotWorsePrice(_type, _market, _outcome, _fxpPrice, _worseOrderId);
            }
        }
        if (_betterOrderId == bytes32(0) && _worseOrderId == bytes32(0)) {
            return (descendOrderList(_type, _market, _outcome, _fxpPrice, _bestOrderId));
        } else if (_betterOrderId == bytes32(0)) {
            return (ascendOrderList(_type, _market, _outcome, _fxpPrice, _worseOrderId));
        } else if (_worseOrderId == bytes32(0)) {
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
