pragma solidity ^0.4.13;

// NOTE: We're using address[100] to get back orderIDs from the orderFetcher as Solidity currently lacks
// the ability to receive dynamic arrays from external contract calls. The list gets shrunk to the desired size
// before returning

import 'ROOT/libraries/arrays/Uint256Arrays.sol';
import 'ROOT/Controller.sol';


// FIXME: Remove this stub once the contract is converted to Solidity
contract OrdersFetcher {
    function getOrderIDs(uint256 _type, address _marketID, uint256 _outcomeID, address _startingOrderID, uint256 _numOrdersToLoad) returns (address[100]);
    function getOrder(address _orderID, uint256 _type, address _marketID, uint256 _outcomeID) returns (uint256[8]);
}


contract OrderBook is Controlled {
    using Uint256Arrays for uint256[];

    function getOrderBook(uint256 _type, address _marketID, uint256 _outcomeID, address _startingOrderID, uint256 _numOrdersToLoad) constant public returns (uint256[] _orderBook) {
        OrdersFetcher _ordersFetcher = OrdersFetcher(controller.lookup("ordersFetcher"));
        address[100] memory _orders = _ordersFetcher.getOrderIDs(_type, _marketID, _outcomeID, _startingOrderID, _numOrdersToLoad);
        _orderBook = new uint256[](8 * _numOrdersToLoad);
        uint8 _numAvailableOrders = 0;
        uint8 _i = 0;
        while (_i < _numOrdersToLoad) {
            // FIXME: Once ordersFetcher.se is converted to solidity make the return value here an 8-tuple and unpack it
            uint256[8] memory _orderInfo = _ordersFetcher.getOrder(_orders[_i], _type, _marketID, _outcomeID);
            if (_orderInfo[0] != 0) {
                uint8 _j = 0;
                while (_j < 8) {
                    _orderBook[8 * _numAvailableOrders + _j] = _orderInfo[_j];
                    _j++;
                }
                _numAvailableOrders++;
            }
            _i++;
        }
        return(_orderBook.slice(0, 8 * _numAvailableOrders));
    }
}