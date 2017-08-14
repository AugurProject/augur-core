/**
 * Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE
 */

pragma solidity ^0.4.13;

import 'ROOT/Controller.sol';
import 'ROOT/libraries/math/SafeMathUint256.sol';
import 'ROOT/trading/Interfaces.sol';
import 'ROOT/trading/OrdersFetcher.sol';


/**
 * @title Orders
 * @dev Storage of all data associated with orders
 */
contract Orders is Controlled {
    using SafeMathUint256 for uint256;

    event CancelOrder(address indexed market, address indexed sender, uint256 fxpPrice, uint256 fxpAmount, uint256 orderId, uint256 outcome, uint256 orderType, uint256 cashRefund, uint256 sharesRefund);
    event CompleteSets(address indexed sender, address indexed market, uint256 indexed orderType, uint256 fxpAmount, uint256 numOutcomes, uint256 marketCreatorFee, uint256 reportingFee);
    event MakeOrder(address indexed market, address indexed sender, uint256 indexed orderType, uint256 fxpPrice, uint256 fxpAmount, uint256 outcome, uint256 orderId, uint256 fxpMoneyEscrowed, uint256 fxpSharesEscrowed, uint256 tradeGroupId);
    event TakeOrder(address indexed market, uint256 indexed outcome, uint256 indexed orderType, uint256 orderId, uint256 price, address maker, address taker, uint256 makerShares, uint256 makerTokens, uint256 takerShares, uint256 takerTokens, uint256 tradeGroupId);

    struct Order {
        uint256 fxpAmount;
        uint256 fxpPrice;
        address owner;
        uint256 fxpSharesEscrowed;
        uint256 fxpMoneyEscrowed;
        uint256 betterOrderId;
        uint256 worseOrderId;
        uint256 gasPrice;
    }

    struct MarketOrders {
        uint256 volume;
        uint256[] prices;
    }

    // Trade types
    // FIXME: Ideally, this should probably be an enum
    uint8 private constant BID = 1;
    uint8 private constant ASK = 2;

    mapping(address => mapping(uint8 => mapping(uint256 => mapping(uint256 => Order)))) private orders;
    mapping(address => MarketOrders) private marketOrderData;
    mapping(address => mapping(uint8 => mapping(uint256 => uint256))) private bestOrder;
    mapping(address => mapping(uint8 => mapping(uint256 => uint256))) private worstOrder;

    // Getters
    function getOrders(uint256 _orderId, uint256 _type, Market _market, uint8 _outcome) public constant returns (uint256, uint256, address, uint256, uint256, uint256, uint256, uint256) {
        Order _order = orders[_market][_outcome][_type][_orderId];
        return (_order.fxpAmount, _order.fxpPrice, _order.owner, _order.fxpSharesEscrowed, _order.fxpMoneyEscrowed, _order.betterOrderId, _order.worseOrderId, _order.gasPrice);
    }

    function getMarketOrderData(Market _market) public constant returns (uint256, uint256[]) {
        return (marketOrderData[_market].volume, marketOrderData[_market].prices);
    }

    function getBestOrders(uint256 _type, Market _market, uint8 _outcome) public constant returns (uint256) {
        return bestOrder[_market][_outcome][_type];
    }

    function getWorstOrders(uint256 _type, Market _market, uint8 _outcome) public constant returns (uint256) {
        return worstOrder[_market][_outcome][_type];
    }

    function getAmount(uint256 _orderId, uint256 _type, Market _market, uint8 _outcome) public constant returns (uint256) { 
        return orders[_market][_outcome][_type][_orderId].fxpAmount;
    }

    function getPrice(uint256 _orderId, uint256 _type, Market _market, uint8 _outcome) public constant returns (uint256) {
        return orders[_market][_outcome][_type][_orderId].fxpPrice;
    }

    function getOrderOwner(uint256 _orderId, uint256 _type, Market _market, uint8 _outcome) public constant returns (address) { 
        return orders[_market][_outcome][_type][_orderId].owner;
    }

    function getOrderSharesEscrowed(uint256 _orderId, uint256 _type, Market _market, uint8 _outcome) public constant returns (uint256) { 
        return orders[_market][_outcome][_type][_orderId].fxpSharesEscrowed;
    }

    function getOrderMoneyEscrowed(uint256 _orderId, uint256 _type, Market _market, uint8 _outcome) public constant returns (uint256) { 
        return orders[_market][_outcome][_type][_orderId].fxpMoneyEscrowed;
    }

    function getVolume(Market _market) public constant returns (uint256) { 
        return marketOrderData[_market].volume;
    }

    function getLastOutcomePrice(Market _market, uint8 _outcome) public constant returns (uint256) { 
        return marketOrderData[_market].prices[_outcome];
    }

    function getBetterOrderId(uint256 _orderId, uint256 _type, Market _market, uint8 _outcome) public constant returns (uint256) { 
        return orders[_market][_outcome][_type][_orderId].betterOrderId;
    }

    function getWorseOrderId(uint256 _orderId, uint256 _type, Market _market, uint8 _outcome) public constant returns (uint256) {
        return orders[_market][_outcome][_type][_orderId].worseOrderId;
    }

    function getGasPrice(uint256 _orderId, uint256 _type, Market _market, uint8 _outcome) public constant returns (uint256) { 
        return orders[_market][_outcome][_type][_orderId].gasPrice;
    }

    function getBestOrderId(uint256 _type, Market _market, uint8 _outcome) public constant returns (uint256) { 
        return bestOrder[_market][_outcome][_type];
    }

    function getWorstOrderId(uint256 _type, Market _market, uint8 _outcome) public constant returns (uint256) { 
        return worstOrder[_market][_outcome][_type];
    }

    function isBetterPrice(uint256 _type, Market _market, uint8 _outcome, uint256 _fxpPrice, uint256 _orderId) public constant returns (bool) { 
        if (_type == BID) { 
            return (_fxpPrice > orders[_market][_outcome][_type][_orderId].fxpPrice);
        } else {
            return (_fxpPrice < orders[_market][_outcome][_type][_orderId].fxpPrice);
        }
    }

    function isWorsePrice(uint256 _type, Market _market, uint8 _outcome, uint256 _fxpPrice, uint256 _orderId) public constant returns (bool) { 
        if (_type == BID) { 
            return (_fxpPrice < orders[_market][_outcome][_type][_orderId].fxpPrice);
        } else {
            return (_fxpPrice > orders[_market][_outcome][_type][_orderId].fxpPrice);
        }
    }

    function assertIsNotBetterPrice(uint256 _type, Market _market, uint8 _outcome, uint256 _fxpPrice, uint256 _betterOrderId) public constant returns (bool) { 
        require(!isBetterPrice(_type, _market, _outcome, _fxpPrice, _betterOrderId));
        return true;
    }

    function assertIsNotWorsePrice(uint256 _type, Market _market, uint8 _outcome, uint256 _fxpPrice, uint256 _worseOrderId) public returns (bool) { 
        require(!isWorsePrice(_type, _market, _outcome, _fxpPrice, _worseOrderId));
        return true;
    }

    function insertOrderIntoList(uint256 _orderId, uint256 _type, Market _market, uint8 _outcome, uint256 _fxpPrice, uint256 _betterOrderId, uint256 _worseOrderId) internal onlyWhitelistedCallers returns (bool) { 
        uint256 _bestOrderId = bestOrder[_market][_outcome][_type];
        uint256 _worstOrderId = worstOrder[_market][_outcome][_type];
        var ordersFetcher = OrdersFetcher(controller.lookup('OrdersFetcher'));
        (_betterOrderId, _worseOrderId) = ordersFetcher.findBoundingOrders(_type, _market, _outcome, _fxpPrice, _bestOrderId, _worstOrderId, _betterOrderId, _worseOrderId);
        if (_type == BID) { 
            _bestOrderId = updateBestBidOrder(_orderId, _market, _fxpPrice, _outcome);
            _worstOrderId = updateWorstBidOrder(_orderId, _market, _fxpPrice, _outcome);
        } else {
            _bestOrderId = updateBestAskOrder(_orderId, _market, _fxpPrice, _outcome);
            _worstOrderId = updateWorstAskOrder(_orderId, _market, _fxpPrice, _outcome);
        }
        if (_bestOrderId == _orderId) { 
            _betterOrderId = 0;
        }
        if (_worstOrderId == _orderId) { 
            _worseOrderId = 0;
        }
        if (_betterOrderId != 0) { 
            orders[_market][_outcome][_type][_betterOrderId].worseOrderId = _orderId;
            orders[_market][_outcome][_type][_orderId].betterOrderId = _betterOrderId;
        }
        if (_worseOrderId != 0) { 
            orders[_market][_outcome][_type][_worseOrderId].betterOrderId = _orderId;
            orders[_market][_outcome][_type][_orderId].worseOrderId = _worseOrderId;
        }
        return true;
    }

    function saveOrder(uint256 _orderId, uint256 _type, Market _market, uint256 _fxpAmount, uint256 _fxpPrice, address _sender, uint8 _outcome, uint256 _fxpMoneyEscrowed, uint256 _fxpSharesEscrowed, uint256 _betterOrderId, uint256 _worseOrderId, uint256 _gasPrice) public onlyWhitelistedCallers returns (bool) { 
        require(_type == BID || _type == ASK);
        require(0 <= _outcome || _outcome < _market.getNumberOfOutcomes());
        insertOrderIntoList(_orderId, _type, _market, _outcome, _fxpPrice, _betterOrderId, _worseOrderId);
        orders[_market][_outcome][_type][_orderId].fxpPrice = _fxpPrice;
        orders[_market][_outcome][_type][_orderId].fxpAmount = _fxpAmount;
        orders[_market][_outcome][_type][_orderId].owner = _sender;
        orders[_market][_outcome][_type][_orderId].fxpMoneyEscrowed = _fxpMoneyEscrowed;
        orders[_market][_outcome][_type][_orderId].fxpSharesEscrowed = _fxpSharesEscrowed;
        orders[_market][_outcome][_type][_orderId].gasPrice = _gasPrice;
        return true;
    }

    function removeOrder(uint256 _orderId, uint256 _type, Market _market, uint8 _outcome) public onlyWhitelistedCallers returns (bool) { 
        require(tx.gasprice <= orders[_market][_outcome][_type][_orderId].gasPrice);
        removeOrderFromList(_orderId, _type, _market, _outcome);
        orders[_market][_outcome][_type][_orderId].fxpPrice = 0;
        orders[_market][_outcome][_type][_orderId].fxpAmount = 0;
        orders[_market][_outcome][_type][_orderId].owner = 0;
        orders[_market][_outcome][_type][_orderId].fxpMoneyEscrowed = 0;
        orders[_market][_outcome][_type][_orderId].fxpSharesEscrowed = 0;
        orders[_market][_outcome][_type][_orderId].gasPrice = 0;
        return true;
    }

    function fillOrder(uint256 _orderId, uint256 _orderType, Market _market, uint8 _orderOutcome, uint256 _sharesFilled, uint256 _tokensFilled) public onlyWhitelistedCallers returns (bool) { 
        // FIXME: Should eventually be changed to `require(_market.getTypeName() == "Market")`
        require(_market != address(0));
        require(0 <= _orderOutcome && _orderOutcome < _market.getNumberOfOutcomes());
        require(_orderType == BID || _orderType == ASK);
        require(_orderId != 0);
        require(_sharesFilled <= orders[_market][_orderOutcome][_orderType][_orderId].fxpSharesEscrowed);
        require(_tokensFilled <= orders[_market][_orderOutcome][_orderType][_orderId].fxpMoneyEscrowed);
        require(tx.gasprice <= orders[_market][_orderOutcome][_orderType][_orderId].gasPrice);
        require(orders[_market][_orderOutcome][_orderType][_orderId].fxpPrice <= _market.getMaxDisplayPrice());
        require(orders[_market][_orderOutcome][_orderType][_orderId].fxpPrice >= _market.getMinDisplayPrice());
        require(_market.getMaxDisplayPrice() + _market.getMinDisplayPrice() <= 2**254);
        uint256 _fill = 0;
        if (_orderType == BID) {
            // We can't use safeSub here because it disallows subtracting negative numbers. Worst case here is an operation of 2**254 - 1 as required above, which won't overflow
            _fill = _sharesFilled + (_tokensFilled.fxpDiv(orders[_market][_orderOutcome][_orderType][_orderId].fxpPrice - _market.getMinDisplayPrice()));
        }
        if (_orderType == ASK) {
            // We can't use safeSub here because it disallows subtracting negative numbers. Worst case here is an operation of 2**254 - 1 as required above, which won't overflow
            _fill = _sharesFilled + (_tokensFilled.fxpDiv(_market.getMaxDisplayPrice() - orders[_market][_orderOutcome][_orderType][_orderId].fxpPrice));
        }
        require(_fill <= orders[_market][_orderOutcome][_orderType][_orderId].fxpAmount);
        orders[_market][_orderOutcome][_orderType][_orderId].fxpAmount -= _fill;
        orders[_market][_orderOutcome][_orderType][_orderId].fxpMoneyEscrowed -= _tokensFilled;
        orders[_market][_orderOutcome][_orderType][_orderId].fxpSharesEscrowed -= _sharesFilled;
        if (orders[_market][_orderOutcome][_orderType][_orderId].fxpAmount == 0) {
            require(orders[_market][_orderOutcome][_orderType][_orderId].fxpMoneyEscrowed == 0);
            require(orders[_market][_orderOutcome][_orderType][_orderId].fxpSharesEscrowed == 0);
            removeOrderFromList(_orderId, _orderType, _market, _orderOutcome);
            orders[_market][_orderOutcome][_orderType][_orderId].fxpPrice = 0;
            orders[_market][_orderOutcome][_orderType][_orderId].owner = 0;
            orders[_market][_orderOutcome][_orderType][_orderId].gasPrice = 0;
            orders[_market][_orderOutcome][_orderType][_orderId].betterOrderId = 0;
            orders[_market][_orderOutcome][_orderType][_orderId].worseOrderId = 0;
        }
        return true;
    }

    function takeOrderLog(Market _market, uint8 _orderOutcome, uint256 _orderType, uint256 _orderId, address _taker, uint256 _makerSharesFilled, uint256 _makerTokensFilled, uint256 _takerSharesFilled, uint256 _takerTokensFilled, uint256 _tradeGroupId) internal constant returns (bool) { 
        uint256 _price = orders[_market][_orderOutcome][_orderType][_orderId].fxpPrice;
        address _maker = orders[_market][_orderOutcome][_orderType][_orderId].owner;
        TakeOrder(_market, _orderOutcome, _orderType, _orderId, _price, _maker, _taker, _makerSharesFilled, _makerTokensFilled, _takerSharesFilled, _takerTokensFilled, _tradeGroupId);
        return true;
    }

    function completeSetsLog(address _sender, Market _market, uint256 _type, uint256 _fxpAmount, uint256 _numOutcomes, uint256 _marketCreatorFee, uint256 _reportingFee) internal constant returns (bool) { 
        CompleteSets(_sender, _market, _type, _fxpAmount, _numOutcomes, _marketCreatorFee, _reportingFee);
        return true;
    }

    function cancelOrderLog(Market _market, address _sender, uint256 _fxpPrice, uint256 _fxpAmount, uint256 _orderId, uint8 _outcome, uint256 _type, uint256 _fxpMoneyEscrowed, uint256 _fxpSharesEscrowed) internal constant returns (uint256) { 
        CancelOrder(_market, _sender, _fxpPrice, _fxpAmount, _orderId, _outcome, _type, _fxpMoneyEscrowed, _fxpSharesEscrowed);
        return 1;
    }

    function modifyMarketVolume(Market _market, uint256 _fxpAmount) internal returns (bool) { 
        marketOrderData[_market].volume += _fxpAmount;
        _market.getBranch().getTopics().updatePopularity(_market.getTopic(), _fxpAmount);
        return true;
    }

    function setPrice(Market _market, uint8 _outcome, uint256 _fxpPrice) internal returns (uint256) { 
        marketOrderData[_market].prices[_outcome] = _fxpPrice;
        return 1;
    }

    function removeOrderFromList(uint256 _orderId, uint256 _type, Market _market, uint8 _outcome) private returns (bool) { 
        uint256 _betterOrderId = orders[_market][_outcome][_type][_orderId].betterOrderId;
        uint256 _worseOrderId = orders[_market][_outcome][_type][_orderId].worseOrderId;
        if (bestOrder[_market][_outcome][_type] == _orderId) { 
            bestOrder[_market][_outcome][_type] = _worseOrderId;
        }
        if (worstOrder[_market][_outcome][_type] == _orderId) { 
            worstOrder[_market][_outcome][_type] = _betterOrderId;
        }
        if (_betterOrderId != 0) { 
            orders[_market][_outcome][_type][_betterOrderId].worseOrderId = _worseOrderId;
        }
        if (_worseOrderId != 0) { 
            orders[_market][_outcome][_type][_worseOrderId].betterOrderId = _betterOrderId;
        }
        orders[_market][_outcome][_type][_orderId].betterOrderId = 0;
        orders[_market][_outcome][_type][_orderId].worseOrderId = 0;
        return true;
    }

    /**
     * @dev If best bid is not set or price higher than best bid price, this order is the new best bid.
     */
    function updateBestBidOrder(uint256 _orderId, Market _market, uint256 _fxpPrice, uint8 _outcome) private returns (uint256) { 
        uint256 _bestBidOrderId = bestOrder[_market][_outcome][BID];
        if (_bestBidOrderId == 0 || _fxpPrice > orders[_market][_outcome][BID][_bestBidOrderId].fxpPrice) { 
            bestOrder[_market][_outcome][BID] = _orderId;
        }
        return bestOrder[_market][_outcome][BID];
    }

    /**
     * @dev If worst bid is not set or price lower than worst bid price, this order is the new worst bid.
     */
    function updateWorstBidOrder(uint256 _orderId, Market _market, uint256 _fxpPrice, uint8 _outcome) private returns (uint256) { 
        uint256 _worstBidOrderId = worstOrder[_market][_outcome][BID];
        if (_worstBidOrderId == 0 || _fxpPrice < orders[_market][_outcome][BID][_worstBidOrderId].fxpPrice) { 
            worstOrder[_market][_outcome][BID] = _orderId;
        }
        return worstOrder[_market][_outcome][BID];
    }

    /**
     * @dev If best ask is not set or price lower than best ask price, this order is the new best ask.
     */
    function updateBestAskOrder(uint256 _orderId, Market _market, uint256 _fxpPrice, uint8 _outcome) private returns (uint256) { 
        uint256 _bestAskOrderId = bestOrder[_market][_outcome][ASK];
        if (_bestAskOrderId == 0 || _fxpPrice < orders[_market][_outcome][ASK][_bestAskOrderId].fxpPrice) { 
            bestOrder[_market][_outcome][ASK] = _orderId;
        }
        return bestOrder[_market][_outcome][ASK];
    }

    /**
     * @dev If worst ask is not set or price higher than worst ask price, this order is the new worst ask.
     */
    function updateWorstAskOrder(uint256 _orderId, Market _market, uint256 _fxpPrice, uint8 _outcome) private returns (uint256) {
        uint256 _worstAskOrderId = worstOrder[_market][_outcome][ASK];
        if (_worstAskOrderId == 0 || _fxpPrice > orders[_market][_outcome][ASK][_worstAskOrderId].fxpPrice) { 
            worstOrder[_market][_outcome][ASK] = _orderId;
        }
        return worstOrder[_market][_outcome][ASK];
    }
}
