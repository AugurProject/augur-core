pragma solidity ^0.4.13;

// NOTE: We're using uint256[100] to get back orderIds from the orderFetcher as Solidity currently lacks the ability to receive dynamic arrays from external contract calls. Really we should not be returning arbitrary size arrays from internal contracts anywhere. The list gets shrunk to the desired size before returning

import 'ROOT/libraries/arrays/Uint256Arrays.sol';
import 'ROOT/Controller.sol';
import 'ROOT/reporting/Market.sol';
import 'ROOT/reporting/Interfaces.sol';


// FIXME: Remove this stub once the contract is converted to Solidity
contract OrdersFetcher {
    function getOrderIDs(uint256 _type, Market _market, uint256 _outcome, uint256 _startingOrderId, uint256 _numOrdersToLoad) returns (uint256[100]);
    function getOrder(uint256 _orderId, uint256 _type, Market _market, uint256 _outcome) returns (uint256[8]);
}


contract OrderBook is Controlled {
    using Uint256Arrays for uint256[];

    function getOrderBook(uint256 _type, Market _market, uint256 _outcome, uint256 _startingOrderId, uint256 _numOrdersToLoad) constant public returns (uint256[] _orderBook) {
        OrdersFetcher _ordersFetcher = OrdersFetcher(controller.lookup("OrdersFetcher"));
        uint256[100] memory _orders = _ordersFetcher.getOrderIDs(_type, _market, _outcome, _startingOrderId, _numOrdersToLoad);
        _orderBook = new uint256[](9 * _numOrdersToLoad);
        uint8 _numAvailableOrders = 0;
        uint8 _i = 0;
        while (_i < _numOrdersToLoad) {
            // FIXME: Once ordersFetcher.se is converted to solidity make the return value here an 8-tuple and unpack it
            uint256[8] memory _orderInfo = _ordersFetcher.getOrder(_orders[_i], _type, _market, _outcome);
            if (_orderInfo[0] != 0) {
                _orderBook[9 * _numAvailableOrders] = _orders[_i];
                uint8 _j = 1;
                while (_j < 9) {
                    _orderBook[9 * _numAvailableOrders + _j] = _orderInfo[_j - 1];
                    _j++;
                }
                _numAvailableOrders++;
            }
            _i++;
        }
        return(_orderBook.slice(0, 9 * _numAvailableOrders));
    }
}
