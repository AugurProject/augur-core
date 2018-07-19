pragma solidity 0.4.20;

import 'trading/IOrders.sol';
import 'reporting/IMarket.sol';


contract OrdersFinder {
    IOrders public orders;

    function OrdersFinder(IOrders _orders) public {
        orders = _orders;
    }

    function getExistingOrders5(Order.Types _type, IMarket _market, uint256 _outcome) external view returns (bytes32[5] _results) {
        bytes32 _orderId = orders.getBestOrderId(_type, _market, _outcome);
        uint256 _index = 0;
        while (_orderId != 0) {
            _results[_index] = _orderId;
            _index++;
            _orderId = orders.getWorseOrderId(_orderId);
        }
        return _results;
    }

    function getExistingOrders10(Order.Types _type, IMarket _market, uint256 _outcome) external view returns (bytes32[10] _results) {
        bytes32 _orderId = orders.getBestOrderId(_type, _market, _outcome);
        uint256 _index = 0;
        while (_orderId != 0) {
            _results[_index] = _orderId;
            _index++;
            _orderId = orders.getWorseOrderId(_orderId);
        }
        return _results;
    }

    function getExistingOrders20(Order.Types _type, IMarket _market, uint256 _outcome) external view returns (bytes32[20] _results) {
        bytes32 _orderId = orders.getBestOrderId(_type, _market, _outcome);
        uint256 _index = 0;
        while (_orderId != 0) {
            _results[_index] = _orderId;
            _index++;
            _orderId = orders.getWorseOrderId(_orderId);
        }
        return _results;
    }

    function getExistingOrders50(Order.Types _type, IMarket _market, uint256 _outcome) external view returns (bytes32[50] _results) {
        bytes32 _orderId = orders.getBestOrderId(_type, _market, _outcome);
        uint256 _index = 0;
        while (_orderId != 0) {
            _results[_index] = _orderId;
            _index++;
            _orderId = orders.getWorseOrderId(_orderId);
        }
        return _results;
    }

    function getExistingOrders100(Order.Types _type, IMarket _market, uint256 _outcome) external view returns (bytes32[100] _results) {
        bytes32 _orderId = orders.getBestOrderId(_type, _market, _outcome);
        uint256 _index = 0;
        while (_orderId != 0) {
            _results[_index] = _orderId;
            _index++;
            _orderId = orders.getWorseOrderId(_orderId);
        }
        return _results;
    }

    function getExistingOrders200(Order.Types _type, IMarket _market, uint256 _outcome) external view returns (bytes32[200] _results) {
        bytes32 _orderId = orders.getBestOrderId(_type, _market, _outcome);
        uint256 _index = 0;
        while (_orderId != 0) {
            _results[_index] = _orderId;
            _index++;
            _orderId = orders.getWorseOrderId(_orderId);
        }
        return _results;
    }

    function getExistingOrders500(Order.Types _type, IMarket _market, uint256 _outcome) external view returns (bytes32[500] _results) {
        bytes32 _orderId = orders.getBestOrderId(_type, _market, _outcome);
        uint256 _index = 0;
        while (_orderId != 0) {
            _results[_index] = _orderId;
            _index++;
            _orderId = orders.getWorseOrderId(_orderId);
        }
        return _results;
    }

    function getExistingOrders1000(Order.Types _type, IMarket _market, uint256 _outcome) external view returns (bytes32[1000] _results) {
        bytes32 _orderId = orders.getBestOrderId(_type, _market, _outcome);
        uint256 _index = 0;
        while (_orderId != 0) {
            _results[_index] = _orderId;
            _index++;
            _orderId = orders.getWorseOrderId(_orderId);
        }
        return _results;
    }
}
