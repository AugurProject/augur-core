/**
 * Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE
 */

pragma solidity ^0.4.13;

import 'ROOT/factories/IterableMapFactory.sol';
import 'ROOT/libraries/arrays/Uint256Arrays.sol';
import 'ROOT/libraries/math/SafeMathUint256.sol';
import 'ROOT/trading/Interfaces.sol';
import 'ROOT/trading/Orders.sol';
import 'ROOT/Controller.sol';

//inset('../macros/externs.sem')
//inset('../macros/require.sem')
//inset('../macros/assertNoValue.sem')
//inset('../macros/orderFields.sem')


contract OrdersFetcher is Controlled {
    using Uint256Arrays for uint256[];

    struct Order {
        uint256 fxpAmount;
        uint256 fxpPrice;
        address owner;
        uint256 fxpSharesEscrowed;
        uint256 fxpMoneyEscrowed;
        address betterOrderId;
        address worseOrderId;
        uint256 gasPrice;
    }

    // Trade types
    uint8 private constant BID = 1;
    uint8 private constant ASK = 2;

    mapping(address => mapping(uint256 => mapping(uint256 => mapping(address => Order)))) private orders;

    // data controller
    // data owner
    // data initialized

    // function init() {
    //     self.owner = msg.sender;
    // }

    // function any() {
    //     assertNoValue();
    // }

    // function initialize(address _controller) {
    //     require(msg.sender == owner);
    //     require(not initialized);
    //     self.initialized = 1;
    //     self.controller = controller;
    // }

    /**
     * @dev Get orders for a particular market, type, and outcome (chunked)
     * @public
     */
    function getOrderIds(uint256 _type, Market _market, uint256 _outcome, address _startingOrderId, uint256 _numOrdersToLoad) {
        require(_type == BID || _type == ASK);
        require(0 <= _outcome && _outcome < _market.getNumberOfOutcomes());
        var _orders = Orders(controller.lookup('Orders'));
        if (_startingOrderId == 0) {
            _startingOrderId = Orders.getBestOrderID(_type, _market, _outcome);
        }
        //_orderIds = array(_numOrdersToLoad);
        uint256[] _orderIds;
        _orderIds[0] = _startingOrderId;
        uint256 _i = 0;
        while (_i < _numOrdersToLoad && orders.getWorseOrderID(_orderIds[_i], _type, _market, _outcome) != 0) {
            _orderIds[_i + 1] = orders.getWorseOrderID(_orderIds[_i], _type, _market, _outcome);
            _i += 1;
        }
        return (_orderIds.slice(0, _i));
    }

    /**
     * @public
     * TODO: _type should be an enum with two options and _outcome should be a uint8.
     */
    function getOrder(address _orderId, uint256 _type, Market _market, uint256 _outcome) returns (uint256, uint256, address, uint256, uint256, address, address, uint256) {
        uint256 _attoshares = orders.getAmount(_orderId, _type, _market, _outcome);
        uint256 _displayPrice = orders.getPrice(_orderId, _type, _market, _outcome);
        address _owner = orders.getOrderOwner(_orderId, _type, _market, _outcome);
        uint256 _tokensEscrowed = orders.getOrderMoneyEscrowed(_orderId, _type, _market, _outcome);
        uint256 _sharesEscrowed = orders.getOrderSharesEscrowed(_orderId, _type, _market, _outcome);
        address _betterOrderId = orders.getBetterOrderID(_orderId, _type, _market, _outcome);
        address _worseOrderId = orders.getWorseOrderID(_orderId, _type, _market, _outcome);
        uint256 _gasPrice = orders.getGasPrice(_orderId, _type, _market, _outcome);
        return (_attoshares, _displayPrice, _owner, _tokensEscrowed, _sharesEscrowed, _betterOrderId, _worseOrderId, _gasPrice);
    }

    /**
     * @public
     */
    function ascendOrderList(int256 _type, address _market, uint256 _outcome, uint256 _fxpPrice, address _lowestOrderId) constant returns (address, address) {
        address _worseOrderId = _lowestOrderId;
        bool _isWorstPrice;
        if (_type == BID) {
            _isWorstPrice = _fxpPrice <= orders.getPrice(_worseOrderId, _type, _market, _outcome);
        } else {
            _isWorstPrice = _fxpPrice >= orders.getPrice(_worseOrderId, _type, _market, _outcome);
        }
        if (_isWorstPrice) {
            return ([_worseOrderId, orders.getWorseOrderID(_worseOrderId, _type, _market, _outcome)]);
        }
        bool _isBetterPrice = orders.isBetterPrice(_type, _market, _outcome, _fxpPrice, _worseOrderId);
        while(_isBetterPrice && orders.getBetterOrderID(_worseOrderId, _type, _market, _outcome) != 0 && _fxpPrice != orders.getPrice(orders.getBetterOrderID(_worseOrderId, _type, _market, _outcome), _type, _market, _outcome)) {
            _isBetterPrice = orders.isBetterPrice(_type, _market, _outcome, _fxpPrice, orders.getBetterOrderID(_worseOrderId, _type, _market, _outcome));
            if (_isBetterPrice) {
                _worseOrderId = orders.getBetterOrderID(_worseOrderId, _type, _market, _outcome);
            }
        }
        address _betterOrderId = orders.getBetterOrderID(_worseOrderId, _type, _market, _outcome);
        return ([_betterOrderId, _worseOrderId]);
    }

    /**
     * @public
     */
    function descendOrderList(uint256 _type, Market _market, uint256 _outcome, uint256 _fxpPrice, address _highestOrderId) constant returns (address, address) {
        address _betterOrderId = _highestOrderId;
        orders.getPrice(_betterOrderId, _type, _market, _outcome);
        bool _isBestPrice;
        if (_type == BID) {
            _isBestPrice = _fxpPrice > orders.getPrice(_betterOrderId, _type, _market, _outcome);
        } else {
            _isBestPrice = _fxpPrice < orders.getPrice(_betterOrderId, _type, _market, _outcome);
        }
        if (_isBestPrice) {
            return ([0, _betterOrderId]);
        }
        if (_fxpPrice == orders.getPrice(_betterOrderId, _type, _market, _outcome)) {
            return ([_betterOrderId, orders.getWorseOrderID(_betterOrderId, _type, _market, _outcome)]);
        }
        bool _isWorsePrice = orders.isWorsePrice(_type, _market, _outcome, _fxpPrice, _betterOrderId);
        while (_isWorsePrice && orders.getWorseOrderID(_betterOrderId, _type, _market, _outcome) != 0) {
            _isWorsePrice = orders.isWorsePrice(_type, _market, _outcome, _fxpPrice, orders.getWorseOrderID(_betterOrderId, _type, _market, _outcome));
            if (_isWorsePrice || _fxpPrice == orders.getPrice(orders.getWorseOrderID(_betterOrderId, _type, _market, _outcome), _type, _market, _outcome)) {
                _betterOrderId = orders.getWorseOrderID(_betterOrderId, _type, _market, _outcome);
            }
        }
        address _worseOrderId = orders.getWorseOrderID(_betterOrderId, _type, _market, _outcome);
        return ([_betterOrderId, _worseOrderId]);
    }

    /**
     * @public
     */
    function findBoundingOrders(int256 _type, Market _market, int256 _outcome, int256 _fxpPrice, address _bestOrderId, address _worstOrderId, address _betterOrderId, address _worseOrderId) constant returns (address, address) {
        if (_bestOrderId == _worstOrderId) {
            if (_bestOrderId == 0) {
                return ([0, 0]);
            } else if (orders.isBetterPrice(_type, _market, _outcome, _fxpPrice, _bestOrderId)) {
                return ([0, _bestOrderId]);
            } else {
                return ([_bestOrderId, 0]);
            }
        }
        if (_betterOrderId != 0) {
            if (orders.getPrice(_betterOrderId, _type, _market, _outcome) == 0) {
                _betterOrderId = 0;
            } else {
                orders.assertIsNotBetterPrice(_type, _market, _outcome, _fxpPrice, _betterOrderId);
            }
        }
        if (_worseOrderId != 0) {
            if (orders.getPrice(_worseOrderId, _type, _market, _outcome) == 0) {
                _worseOrderId = 0;
            } else {
                orders.assertIsNotWorsePrice(_type, _market, _outcome, _fxpPrice, _worseOrderId);
            }
        }
        if (_betterOrderId == 0 && _worseOrderId == 0) {
            return (descendOrderList(_type, _market, _outcome, _fxpPrice, _bestOrderId));
        } else if (_betterOrderId == 0) {
            return (ascendOrderList(_type, _market, _outcome, _fxpPrice, _worseOrderId));
        } else if (_worseOrderId == 0) {
            return (descendOrderList(_type, _market, _outcome, _fxpPrice, _betterOrderId));
        }
        if (orders.getWorseOrderID(_betterOrderId, _type, _market, _outcome) != _worseOrderId) {
            return (descendOrderList(_type, _market, _outcome, _fxpPrice, _betterOrderId));
        } else if (orders.getBetterOrderID(_worseOrderId, _type, _market, _outcome) != _betterOrderId) {
            return (ascendOrderList(_type, _market, _outcome, _fxpPrice, _worseOrderId));
        }
        return ([_betterOrderId, _worseOrderId]);
    }
}
