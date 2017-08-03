/**
 * Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE
 */

pragma solidity ^0.4.13;

import 'ROOT/libraries/math/SafeMath.sol';
import 'ROOT/factories/IterableMapFactory.sol';
import 'ROOT/Controller.sol';


// FIXME: remove stubs once these can be imported as a solidty contracts
contract OrdersFetcher {
    function findBoundingOrders(int256 _type, Market _market, int256 _outcome, int256 _fxpPrice, address _bestOrderID, address _worstOrderID, address _betterOrderID, address _worseOrderID) returns (address, address);
}


contract Market {
    int256 private numOutcomes;
    int256 private maxDisplayPrice;
    int256 private minDisplayPrice;
    ReportingWindow private reportingWindow;
    int256 private topic;

    function getNumberOfOutcomes() public constant returns (int256) {
        return numOutcomes;
    }

    function getMaxDisplayPrice() public constant returns (int256) {
        return maxDisplayPrice;
    }

    function getMinDisplayPrice() public constant returns (int256) {
        return minDisplayPrice;
    }

    function getReportingWindow() public constant returns (ReportingWindow) {
        return reportingWindow;
    }

    function getBranch() public constant returns (Branch) {
        return reportingWindow.getBranch();
    }

    function getTopic() public constant returns(int256) {
        return topic;
    }
}


contract ReportingWindow {
    Branch private branch;

    function getBranch() public constant returns (Branch) {
        return branch;
    }
}


contract Branch {
    Topics topics;

    function getTopics() public constant returns (Topics) {
        return topics;
    }
}


contract Topics is Controlled {
    IterableMap topics;
    IterableMapFactory iterableMapFactory;

    function updatePopularity(int256 _topic, int256 _fxpAmount) onlyWhitelistedCallers returns (bool) {
        // _oldAmount = topics.getByKeyOrZero(_topic);
        // _newAmount = safeAdd(_oldAmount, _fxpAmount);
        // topics.addOrUpdate(_topic, _newAmount);
        return(true);
    }
}


/**
 * @title Orders
 * @dev Storage of all data associated with orders
 */
contract Orders is Controlled {
    using SafeMath for int256;

    event CancelOrder(address indexed market, address indexed sender, int256 fxpPrice, int256 fxpAmount, address orderID, int256 outcome, int256 orderType, int256 cashRefund, int256 sharesRefund);
    event CompleteSets(address indexed sender, address indexed market, int256 indexed orderType, int256 fxpAmount, int256 numOutcomes, int256 marketCreatorFee, int256 reportingFee);
    event MakeOrder(address indexed market, address indexed sender, int256 indexed orderType, int256 fxpPrice, int256 fxpAmount, int256 outcome, address orderID, int256 fxpMoneyEscrowed, int256 fxpSharesEscrowed, int256 tradeGroupID);
    event TakeOrder(address indexed market, int256 indexed outcome, int256 indexed orderType, address orderID, int256 price, address maker, address taker, int256 makerShares, int256 makerTokens, int256 takerShares, int256 takerTokens, int256 tradeGroupID);

    struct Order {
        int256 fxpAmount;
        int256 fxpPrice;
        address owner;
        int256 fxpSharesEscrowed;
        int256 fxpMoneyEscrowed;
        address betterOrderID;
        address worseOrderID;
        uint256 gasPrice;
    }
    struct MarketOrders {
        int256 volume;
        int256[] prices;
    }

    mapping(address => mapping(int256 => mapping(int256 => mapping(address => Order)))) private orders;
    mapping(address => MarketOrders) private marketOrderData;
    mapping(address => mapping(int256 => mapping(int256 => address))) private bestOrder;
    mapping(address => mapping(int256 => mapping(int256 => address))) private worstOrder;

    // Trade types
    int256 private constant BID = 1;
    int256 private constant ASK = 2;

    // Getters
    function getOrders(address _orderID, int256 _type, Market _market, int256 _outcome) public constant returns (int256, int256, address, int256, int256, address, address, uint256) {
        Order _order = orders[_market][_outcome][_type][_orderID];
        return (_order.fxpAmount, _order.fxpPrice, _order.owner, _order.fxpSharesEscrowed, _order.fxpMoneyEscrowed, _order.betterOrderID, _order.worseOrderID, _order.gasPrice);
    }

    function getMarketOrderData(Market _market) public constant returns (int256, int256[]) {
        return (marketOrderData[_market].volume, marketOrderData[_market].prices);
    }

    function getBestOrders(int256 _type, Market _market, int256 _outcome) public constant returns (address) {
        return(bestOrder[_market][_outcome][_type]);
    }

    function getWorstOrders(int256 _type, Market _market, int256 _outcome) public constant returns (address) {
        return(worstOrder[_market][_outcome][_type]);
    }

    // FIXME: We should delete the getters below and replace them with the getters above
    function getAmount(address _orderID, int256 _type, Market _market, int256 _outcome) public constant returns (int256) { 
        return(orders[_market][_outcome][_type][_orderID].fxpAmount);
    }

    function getPrice(address _orderID, int256 _type, Market _market, int256 _outcome) public constant returns (int256) { 
        return(orders[_market][_outcome][_type][_orderID].fxpPrice);
    }

    function getOrderOwner(address _orderID, int256 _type, Market _market, int256 _outcome) public constant returns (address) { 
        return(orders[_market][_outcome][_type][_orderID].owner);
    }

    function getOrderSharesEscrowed(address _orderID, int256 _type, Market _market, int256 _outcome) public constant returns (int256) { 
        return(orders[_market][_outcome][_type][_orderID].fxpSharesEscrowed);
    }

    function getOrderMoneyEscrowed(address _orderID, int256 _type, Market _market, int256 _outcome) public constant returns (int256) { 
        return(orders[_market][_outcome][_type][_orderID].fxpMoneyEscrowed);
    }

    function getVolume(Market _market) public constant returns (int256) { 
        return(marketOrderData[_market].volume);
    }

    function getLastOutcomePrice(Market _market, uint256 _outcome) public constant returns (int256) { 
        return(marketOrderData[_market].prices[_outcome]);
    }

    function getBetterOrderID(address _orderID, int256 _type, Market _market, int256 _outcome) public constant returns (address) { 
        return(orders[_market][_outcome][_type][_orderID].betterOrderID);
    }

    function getWorseOrderID(address _orderID, int256 _type, Market _market, int256 _outcome) public constant returns (address) { 
        return(orders[_market][_outcome][_type][_orderID].worseOrderID);
    }

    function getGasPrice(address _orderID, int256 _type, Market _market, int256 _outcome) public constant returns (uint256) { 
        return(orders[_market][_outcome][_type][_orderID].gasPrice);
    }

    function getBestOrderID(int256 _type, Market _market, int256 _outcome) public constant returns (address) { 
        return(bestOrder[_market][_outcome][_type]);
    }

    function getWorstOrderID(int256 _type, Market _market, int256 _outcome) public constant returns (address) { 
        return(worstOrder[_market][_outcome][_type]);
    }

    function isBetterPrice(int256 _type, Market _market, int256 _outcome, int256 _fxpPrice, address _orderID) public constant returns (bool) { 
        if (_type == BID) { 
            return((_fxpPrice > orders[_market][_outcome][_type][_orderID].fxpPrice));
        } else {
            return((_fxpPrice < orders[_market][_outcome][_type][_orderID].fxpPrice));
        }
    }

    function isWorsePrice(int256 _type, Market _market, int256 _outcome, int256 _fxpPrice, address _orderID) public constant returns (bool) { 
        if (_type == BID) { 
            return((_fxpPrice < orders[_market][_outcome][_type][_orderID].fxpPrice));
        } else {
            return((_fxpPrice > orders[_market][_outcome][_type][_orderID].fxpPrice));
        }
    }

    function assertIsNotBetterPrice(int256 _type, Market _market, int256 _outcome, int256 _fxpPrice, address _betterOrderID) public constant returns (bool) { 
        require(!isBetterPrice(_type, _market, _outcome, _fxpPrice, _betterOrderID));
        return(true);
    }

    function assertIsNotWorsePrice(int256 _type, Market _market, int256 _outcome, int256 _fxpPrice, address _worseOrderID) public returns (bool) { 
        require(!isWorsePrice(_type, _market, _outcome, _fxpPrice, _worseOrderID));
        return(true);
    }

    function insertOrderIntoList(address _orderID, int256 _type, Market _market, int256 _outcome, int256 _fxpPrice, address _betterOrderID, address _worseOrderID) internal onlyWhitelistedCallers returns (bool) { 
        address _bestOrderID = bestOrder[_market][_outcome][_type];
        address _worstOrderID = worstOrder[_market][_outcome][_type];
        var ordersFetcher = OrdersFetcher(controller.lookup('ordersFetcher'));
        (_betterOrderID, _worseOrderID) = ordersFetcher.findBoundingOrders(_type, _market, _outcome, _fxpPrice, _bestOrderID, _worstOrderID, _betterOrderID, _worseOrderID);
        if (_type == BID) { 
            _bestOrderID = updateBestBidOrder(_orderID, _market, _fxpPrice, _outcome);
            _worstOrderID = updateWorstBidOrder(_orderID, _market, _fxpPrice, _outcome);
        } else {
            _bestOrderID = updateBestAskOrder(_orderID, _market, _fxpPrice, _outcome);
            _worstOrderID = updateWorstAskOrder(_orderID, _market, _fxpPrice, _outcome);
        }
        if (_bestOrderID == _orderID) { 
            _betterOrderID = 0;
        }
        if (_worstOrderID == _orderID) { 
            _worseOrderID = 0;
        }
        if (_betterOrderID != 0) { 
            orders[_market][_outcome][_type][_betterOrderID].worseOrderID = _orderID;
            orders[_market][_outcome][_type][_orderID].betterOrderID = _betterOrderID;
        }
        if (_worseOrderID != 0) { 
            orders[_market][_outcome][_type][_worseOrderID].betterOrderID = _orderID;
            orders[_market][_outcome][_type][_orderID].worseOrderID = _worseOrderID;
        }
        return(true);
    }

    function saveOrder(address _orderID, int256 _type, Market _market, int256 _fxpAmount, int256 _fxpPrice, address _sender, int256 _outcome, int256 _fxpMoneyEscrowed, int256 _fxpSharesEscrowed, address _betterOrderID, address _worseOrderID, int256 _tradeGroupID, uint256 _gasPrice) internal onlyWhitelistedCallers returns (bool) { 
        require(_type == BID || _type == ASK);
        require(0 <= _outcome || _outcome < _market.getNumberOfOutcomes());
        insertOrderIntoList(_orderID, _type, _market, _outcome, _fxpPrice, _betterOrderID, _worseOrderID);
        orders[_market][_outcome][_type][_orderID].fxpPrice = _fxpPrice;
        orders[_market][_outcome][_type][_orderID].fxpAmount = _fxpAmount;
        orders[_market][_outcome][_type][_orderID].owner = _sender;
        orders[_market][_outcome][_type][_orderID].fxpMoneyEscrowed = _fxpMoneyEscrowed;
        orders[_market][_outcome][_type][_orderID].fxpSharesEscrowed = _fxpSharesEscrowed;
        orders[_market][_outcome][_type][_orderID].gasPrice = _gasPrice;
        MakeOrder(_market, _sender, _type, _fxpPrice, _fxpAmount, _outcome, _orderID, _fxpMoneyEscrowed, _fxpSharesEscrowed, _tradeGroupID);
        return(true);
    }

    function removeOrder(address _orderID, int256 _type, Market _market, int256 _outcome) internal onlyWhitelistedCallers returns (bool) { 
        require(tx.gasprice <= orders[_market][_outcome][_type][_orderID].gasPrice);
        removeOrderFromList(_orderID, _type, _market, _outcome);
        orders[_market][_outcome][_type][_orderID].fxpPrice = 0;
        orders[_market][_outcome][_type][_orderID].fxpAmount = 0;
        orders[_market][_outcome][_type][_orderID].owner = 0;
        orders[_market][_outcome][_type][_orderID].fxpMoneyEscrowed = 0;
        orders[_market][_outcome][_type][_orderID].fxpSharesEscrowed = 0;
        orders[_market][_outcome][_type][_orderID].gasPrice = 0;
        return(true);
    }

    function fillOrder(address _orderID, int256 _orderType, Market _market, int256 _orderOutcome, int256 _sharesFilled, int256 _tokensFilled) internal onlyWhitelistedCallers returns (bool) { 
        // FIXME: Should eventually be changed to `require(_market.getTypeName() == "Market")`
        require(_market != address(0));
        require(0 <= _orderOutcome && _orderOutcome < _market.getNumberOfOutcomes());
        require(_orderType == BID || _orderType == ASK);
        require(_orderID != 0);
        require(_sharesFilled <= orders[_market][_orderOutcome][_orderType][_orderID].fxpSharesEscrowed);
        require(_tokensFilled <= orders[_market][_orderOutcome][_orderType][_orderID].fxpMoneyEscrowed);
        require(tx.gasprice <= orders[_market][_orderOutcome][_orderType][_orderID].gasPrice);
        require(orders[_market][_orderOutcome][_orderType][_orderID].fxpPrice <= _market.getMaxDisplayPrice());
        require(orders[_market][_orderOutcome][_orderType][_orderID].fxpPrice >= _market.getMinDisplayPrice());
        require(_market.getMaxDisplayPrice() + _market.getMinDisplayPrice() <= 2**254);
        int256 _fill = 0;
        if (_orderType == BID) {
            // We can't use safeSub here because it disallows subtracting negative numbers. Worst case here is an operation of 2**254 - 1 as required above, which won't overflow
            _fill = _sharesFilled + (_tokensFilled.int256Div(orders[_market][_orderOutcome][_orderType][_orderID].fxpPrice - _market.getMinDisplayPrice()));
        }
        if (_orderType == ASK) {
            // We can't use safeSub here because it disallows subtracting negative numbers. Worst case here is an operation of 2**254 - 1 as required above, which won't overflow
            _fill = _sharesFilled + (_tokensFilled.int256Div(_market.getMaxDisplayPrice() - orders[_market][_orderOutcome][_orderType][_orderID].fxpPrice));
        }
        require(_fill <= orders[_market][_orderOutcome][_orderType][_orderID].fxpAmount);
        orders[_market][_orderOutcome][_orderType][_orderID].fxpAmount -= _fill;
        orders[_market][_orderOutcome][_orderType][_orderID].fxpMoneyEscrowed -= _tokensFilled;
        orders[_market][_orderOutcome][_orderType][_orderID].fxpSharesEscrowed -= _sharesFilled;
        if (orders[_market][_orderOutcome][_orderType][_orderID].fxpAmount == 0) {
            require(orders[_market][_orderOutcome][_orderType][_orderID].fxpMoneyEscrowed == 0);
            require(orders[_market][_orderOutcome][_orderType][_orderID].fxpSharesEscrowed == 0);
            removeOrderFromList(_orderID, _orderType, _market, _orderOutcome);
            orders[_market][_orderOutcome][_orderType][_orderID].fxpPrice = 0;
            orders[_market][_orderOutcome][_orderType][_orderID].owner = 0;
            orders[_market][_orderOutcome][_orderType][_orderID].gasPrice = 0;
            orders[_market][_orderOutcome][_orderType][_orderID].betterOrderID = 0;
            orders[_market][_orderOutcome][_orderType][_orderID].worseOrderID = 0;
        }
        return(true);
    }

    function takeOrderLog(Market _market, int256 _orderOutcome, int256 _orderType, address _orderID, address _taker, int256 _makerSharesFilled, int256 _makerTokensFilled, int256 _takerSharesFilled, int256 _takerTokensFilled, int256 _tradeGroupID) internal constant onlyWhitelistedCallers returns (bool) { 
        int256 _price = orders[_market][_orderOutcome][_orderType][_orderID].fxpPrice;
        address _maker = orders[_market][_orderOutcome][_orderType][_orderID].owner;
        TakeOrder(_market, _orderOutcome, _orderType, _orderID, _price, _maker, _taker, _makerSharesFilled, _makerTokensFilled, _takerSharesFilled, _takerTokensFilled, _tradeGroupID);
        return(true);
    }

    function completeSetsLog(address _sender, Market _market, int256 _type, int256 _fxpAmount, int256 _numOutcomes, int256 _marketCreatorFee, int256 _reportingFee) internal constant onlyWhitelistedCallers returns (bool) { 
        CompleteSets(_sender, _market, _type, _fxpAmount, _numOutcomes, _marketCreatorFee, _reportingFee);
        return(true);
    }

    function cancelOrderLog(Market _market, address _sender, int256 _fxpPrice, int256 _fxpAmount, address _orderID, int256 _outcome, int256 _type, int256 _fxpMoneyEscrowed, int256 _fxpSharesEscrowed) internal constant onlyWhitelistedCallers returns (uint256) { 
        CancelOrder(_market, _sender, _fxpPrice, _fxpAmount, _orderID, _outcome, _type, _fxpMoneyEscrowed, _fxpSharesEscrowed);
        return(1);
    }

    function modifyMarketVolume(Market _market, int256 _fxpAmount) internal onlyWhitelistedCallers returns (bool) { 
        marketOrderData[_market].volume += _fxpAmount;
        _market.getBranch().getTopics().updatePopularity(_market.getTopic(), _fxpAmount);
        return(true);
    }

    function setPrice(Market _market, uint256 _outcome, int256 _fxpPrice) internal onlyWhitelistedCallers returns (uint256) { 
        marketOrderData[_market].prices[_outcome] = _fxpPrice;
        return(1);
    }

    function removeOrderFromList(address _orderID, int256 _type, Market _market, int256 _outcome) private returns (bool) { 
        address _betterOrderID = orders[_market][_outcome][_type][_orderID].betterOrderID;
        address _worseOrderID = orders[_market][_outcome][_type][_orderID].worseOrderID;
        if (bestOrder[_market][_outcome][_type] == _orderID) { 
            bestOrder[_market][_outcome][_type] = _worseOrderID;
        }
        if (worstOrder[_market][_outcome][_type] == _orderID) { 
            worstOrder[_market][_outcome][_type] = _betterOrderID;
        }
        if (_betterOrderID != 0) { 
            orders[_market][_outcome][_type][_betterOrderID].worseOrderID = _worseOrderID;
        }
        if (_worseOrderID != 0) { 
            orders[_market][_outcome][_type][_worseOrderID].betterOrderID = _betterOrderID;
        }
        orders[_market][_outcome][_type][_orderID].betterOrderID = 0;
        orders[_market][_outcome][_type][_orderID].worseOrderID = 0;
        return(true);
    }

    /**
     * @dev If best bid is not set or price higher than best bid price, this order is the new best bid.
     */
    function updateBestBidOrder(address _orderID, Market _market, int256 _fxpPrice, int256 _outcome) private returns (address) { 
        address _bestBidOrderID = bestOrder[_market][_outcome][BID];
        if (_bestBidOrderID == 0 || _fxpPrice > orders[_market][_outcome][BID][_bestBidOrderID].fxpPrice) { 
            bestOrder[_market][_outcome][BID] = _orderID;
        }
        return(bestOrder[_market][_outcome][BID]);
    }

    /**
     * @dev If worst bid is not set or price lower than worst bid price, this order is the new worst bid.
     */
    function updateWorstBidOrder(address _orderID, Market _market, int256 _fxpPrice, int256 _outcome) private returns (address) { 
        address _worstBidOrderID = worstOrder[_market][_outcome][BID];
        if (_worstBidOrderID == 0 || _fxpPrice < orders[_market][_outcome][BID][_worstBidOrderID].fxpPrice) { 
            worstOrder[_market][_outcome][BID] = _orderID;
        }
        return(worstOrder[_market][_outcome][BID]);
    }

    /**
     * @dev If best ask is not set or price lower than best ask price, this order is the new best ask.
     */
    function updateBestAskOrder(address _orderID, Market _market, int256 _fxpPrice, int256 _outcome) private returns (address) { 
        address _bestAskOrderID = bestOrder[_market][_outcome][ASK];
        if (_bestAskOrderID == 0 || _fxpPrice < orders[_market][_outcome][ASK][_bestAskOrderID].fxpPrice) { 
            bestOrder[_market][_outcome][ASK] = _orderID;
        }
        return(bestOrder[_market][_outcome][ASK]);
    }

    /**
     * @dev If worst ask is not set or price higher than worst ask price, this order is the new worst ask.
     */
    function updateWorstAskOrder(address _orderID, Market _market, int256 _fxpPrice, int256 _outcome) private returns (address) {
        address _worstAskOrderID = worstOrder[_market][_outcome][ASK];
        if (_worstAskOrderID == 0 || _fxpPrice > orders[_market][_outcome][ASK][_worstAskOrderID].fxpPrice) { 
            worstOrder[_market][_outcome][ASK] = _orderID;
        }
        return(worstOrder[_market][_outcome][ASK]);
    }
}
