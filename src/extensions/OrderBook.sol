pragma solidity ^0.4.13;

// NOTE: We're using uint256[100] to get back orderIds from the orderFetcher as Solidity currently lacks the ability to receive dynamic arrays from external contract calls. Really we should not be returning arbitrary size arrays from internal contracts anywhere. The list gets shrunk to the desired size before returning

import 'ROOT/libraries/arrays/Uint256Arrays.sol';
import 'ROOT/Controlled.sol';
import 'ROOT/reporting/IMarket.sol';
import 'ROOT/trading/IOrders.sol';


contract OrderBook is Controlled {
    using Uint256Arrays for uint256[];

    function getOrderBook(Order.TradeTypes _type, IMarket _market, uint8 _outcome, bytes32 _startingOrderId, uint256 _numOrdersToLoad) constant public returns (uint256[] _orderBook) {
        IOrders _orders = IOrders(controller.lookup("Orders"));
        bytes32 _orderId = _startingOrderId;
        if (_orderId == bytes32(0)) {
            _orderId = _orders.getBestOrderId(_type, _market, _outcome);
        }

        for (uint8 _i = 0; _i < _numOrdersToLoad; ++_i) {
            if (_orderId == bytes32(0)) {
                break;
            }
            uint256[8] memory _order = getOrderAsArray(_orders, _orderId);
            _orderBook[_i * 8 + 0] = _order[0];
            _orderBook[_i * 8 + 1] = _order[1];
            _orderBook[_i * 8 + 2] = _order[2];
            _orderBook[_i * 8 + 3] = _order[3];
            _orderBook[_i * 8 + 4] = _order[4];
            _orderBook[_i * 8 + 5] = _order[5];
            _orderBook[_i * 8 + 6] = _order[6];
            _orderBook[_i * 8 + 7] = _order[7];
            _orderId = _orders.getWorseOrderId(_orderId);
        }
        return _orderBook;
    }

    function getOrderAsArray(IOrders _orders, bytes32 _orderId) private constant returns (uint256[8] _order) {
        var (_amount, _price, _owner, _sharesEscrowed, _tokensEscrowed, _betterOrderId, _worseOrderId) = _orders.getOrders(_orderId);
        return [uint256(_orderId), uint256(_amount), uint256(_price), uint256(_owner), uint256(_sharesEscrowed), uint256(_tokensEscrowed), uint256(_betterOrderId), uint256(_worseOrderId)];
    }
}
