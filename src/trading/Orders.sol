pragma solidity ^0.4.13;

import 'ROOT/trading/IOrders.sol';
import 'ROOT/libraries/DelegationTarget.sol';
import 'ROOT/libraries/math/SafeMathUint256.sol';
import 'ROOT/libraries/math/SafeMathInt256.sol';
import 'ROOT/trading/Order.sol';
import 'ROOT/reporting/IMarket.sol';
import 'ROOT/trading/IOrdersFetcher.sol';


/**
 * @title Orders
 * @dev Storage of all data associated with orders
 */
contract Orders is DelegationTarget, IOrders {
    using Order for Order.Data;
    using SafeMathUint256 for uint256;

    event CancelOrder(address indexed market, address indexed sender, uint256 price, uint256 amount, bytes32 orderId, uint8 outcome, Order.TradeTypes orderType, uint256 cashRefund, uint256 sharesRefund);
    event BuyCompleteSets(address indexed sender, address indexed market, uint256 amount, uint256 numOutcomes);
    event SellCompleteSets(address indexed sender, address indexed market, uint256 amount, uint256 numOutcomes, uint256 marketCreatorFee, uint256 reportingFee);
    event MakeOrder(address indexed market, address indexed sender, Order.TradeTypes indexed orderType, uint256 price, uint256 amount, uint8 outcome, bytes32 orderId, uint256 moneyEscrowed, uint256 sharesEscrowed, uint256 tradeGroupId);
    event TakeOrder(address indexed market, uint8 indexed outcome, Order.TradeTypes indexed orderType, bytes32 orderId, uint256 price, address maker, address taker, uint256 makerShares, uint256 makerTokens, uint256 takerShares, uint256 takerTokens, uint256 tradeGroupId);

    struct MarketOrders {
        uint256 volume;
        mapping(uint8 => uint256) prices;
    }

    mapping(bytes32 => Order.Data) private orders;
    mapping(address => MarketOrders) private marketOrderData;
    mapping(bytes32 => bytes32) private bestOrder;
    mapping(bytes32 => bytes32) private worstOrder;

    // Getters
    // this function doesn't work because delegated contracts can't return tuples or dynamic arrays
    function getOrders(bytes32 _orderId) public constant returns (uint256 _amount, uint256 _displayPrice, address _owner, uint256 _sharesEscrowed, uint256 _tokensEscrowed, bytes32 _betterOrderId, bytes32 _worseOrderId) {
        Order.Data storage _order = orders[_orderId];
        return (_order.amount, _order.price, _order.maker, _order.sharesEscrowed, _order.moneyEscrowed, _order.betterOrderId, _order.worseOrderId);
    }

    function getMarket(bytes32 _orderId) public constant returns (IMarket) {
        return orders[_orderId].market;
    }

    function getTradeType(bytes32 _orderId) public constant returns (Order.TradeTypes) {
        return orders[_orderId].tradeType;
    }

    function getOutcome(bytes32 _orderId) public constant returns (uint8) {
        return orders[_orderId].outcome;
    }

    function getAmount(bytes32 _orderId) public constant returns (uint256) {
        return orders[_orderId].amount;
    }

    function getPrice(bytes32 _orderId) public constant returns (uint256) {
        return orders[_orderId].price;
    }

    function getOrderMaker(bytes32 _orderId) public constant returns (address) {
        return orders[_orderId].maker;
    }

    function getOrderSharesEscrowed(bytes32 _orderId) public constant returns (uint256) {
        return orders[_orderId].sharesEscrowed;
    }

    function getOrderMoneyEscrowed(bytes32 _orderId) public constant returns (uint256) {
        return orders[_orderId].moneyEscrowed;
    }

    function getVolume(IMarket _market) public constant returns (uint256) {
        return marketOrderData[_market].volume;
    }

    function getLastOutcomePrice(IMarket _market, uint8 _outcome) public constant returns (uint256) {
        return marketOrderData[_market].prices[_outcome];
    }

    function getBetterOrderId(bytes32 _orderId) public constant returns (bytes32) {
        return orders[_orderId].betterOrderId;
    }

    function getWorseOrderId(bytes32 _orderId) public constant returns (bytes32) {
        return orders[_orderId].worseOrderId;
    }

    function getBestOrderId(Order.TradeTypes _type, IMarket _market, uint8 _outcome) public constant returns (bytes32) {
        return bestOrder[getBestOrderWorstOrderHash(_market, _outcome, _type)];
    }

    function getWorstOrderId(Order.TradeTypes _type, IMarket _market, uint8 _outcome) public constant returns (bytes32) {
        return worstOrder[getBestOrderWorstOrderHash(_market, _outcome, _type)];
    }

    function getOrderId(Order.TradeTypes _type, IMarket _market, uint256 _amount, uint256 _price, address _sender, uint256 _blockNumber, uint8 _outcome, uint256 _moneyEscrowed, uint256 _sharesEscrowed) public constant returns (bytes32) {
        return sha256(_type, _market, _amount, _price, _sender, _blockNumber, _outcome, _moneyEscrowed, _sharesEscrowed);
    }

    function isBetterPrice(Order.TradeTypes _type, uint256 _price, bytes32 _orderId) public constant returns (bool) {
        require(_type == Order.TradeTypes.Bid || _type == Order.TradeTypes.Ask);
        if (_type == Order.TradeTypes.Bid) {
            return (_price > orders[_orderId].price);
        } else if (_type == Order.TradeTypes.Ask) {
            return (_price < orders[_orderId].price);
        }
    }

    function isWorsePrice(Order.TradeTypes _type, uint256 _price, bytes32 _orderId) public constant returns (bool) {
        if (_type == Order.TradeTypes.Bid) {
            return (_price < orders[_orderId].price);
        } else {
            return (_price > orders[_orderId].price);
        }
    }

    function assertIsNotBetterPrice(Order.TradeTypes _type, uint256 _price, bytes32 _betterOrderId) public constant returns (bool) {
        require(!isBetterPrice(_type, _price, _betterOrderId));
        return true;
    }

    function assertIsNotWorsePrice(Order.TradeTypes _type, uint256 _price, bytes32 _worseOrderId) public returns (bool) {
        require(!isWorsePrice(_type, _price, _worseOrderId));
        return true;
    }

    function insertOrderIntoList(Order.Data storage _order, bytes32 _betterOrderId, bytes32 _worseOrderId) private returns (bool) {
        bytes32 _bestOrderId = bestOrder[getBestOrderWorstOrderHash(_order.market, _order.outcome, _order.tradeType)];
        bytes32 _worstOrderId = worstOrder[getBestOrderWorstOrderHash(_order.market, _order.outcome, _order.tradeType)];
        IOrdersFetcher _ordersFetcher = IOrdersFetcher(controller.lookup("OrdersFetcher"));
        (_betterOrderId, _worseOrderId) = _ordersFetcher.findBoundingOrders(_order.tradeType, _order.price, _bestOrderId, _worstOrderId, _betterOrderId, _worseOrderId);
        if (_order.tradeType == Order.TradeTypes.Bid) {
            _bestOrderId = updateBestBidOrder(_order.id, _order.market, _order.price, _order.outcome);
            _worstOrderId = updateWorstBidOrder(_order.id, _order.market, _order.price, _order.outcome);
        } else {
            _bestOrderId = updateBestAskOrder(_order.id, _order.market, _order.price, _order.outcome);
            _worstOrderId = updateWorstAskOrder(_order.id, _order.market, _order.price, _order.outcome);
        }
        if (_bestOrderId == _order.id) {
            _betterOrderId = bytes32(0);
        }
        if (_worstOrderId == _order.id) {
            _worseOrderId = bytes32(0);
        }
        if (_betterOrderId != bytes32(0)) {
            orders[_betterOrderId].worseOrderId = _order.id;
            _order.betterOrderId = _betterOrderId;
        }
        if (_worseOrderId != bytes32(0)) {
            orders[_worseOrderId].betterOrderId = _order.id;
            _order.worseOrderId = _worseOrderId;
        }
        return true;
    }

    function saveOrder(Order.TradeTypes _type, IMarket _market, uint256 _amount, uint256 price, address _sender, uint8 _outcome, uint256 _moneyEscrowed, uint256 _sharesEscrowed, bytes32 _betterOrderId, bytes32 _worseOrderId, uint256 _tradeGroupId) public onlyWhitelistedCallers returns (bytes32 _orderId) {
        require(_outcome < _market.getNumberOfOutcomes());
        _orderId = getOrderId(_type, _market, _amount, price, _sender, block.number, _outcome, _moneyEscrowed, _sharesEscrowed);
        Order.Data storage _order = orders[_orderId];
        _order.orders = this;
        _order.market = _market;
        _order.id = _orderId;
        _order.tradeType = _type;
        _order.outcome = _outcome;
        _order.price = price;
        _order.amount = _amount;
        _order.maker = _sender;
        _order.moneyEscrowed = _moneyEscrowed;
        _order.sharesEscrowed = _sharesEscrowed;
        insertOrderIntoList(_order, _betterOrderId, _worseOrderId);
        MakeOrder(_market, _sender, _type, price, _amount, _outcome, _orderId, _moneyEscrowed, _sharesEscrowed, _tradeGroupId);
        return _orderId;
    }

    function removeOrder(bytes32 _orderId) public onlyWhitelistedCallers returns (bool) {
        removeOrderFromList(_orderId);
        delete orders[_orderId];
        return true;
    }

    function fillOrder(bytes32 _orderId, uint256 _sharesFilled, uint256 _tokensFilled) public onlyWhitelistedCallers returns (bool) {
        Order.Data storage _order = orders[_orderId];
        require(_order.market.getTypeName() == "Market");
        require(_order.outcome < _order.market.getNumberOfOutcomes());
        require(_order.tradeType == Order.TradeTypes.Bid || _order.tradeType == Order.TradeTypes.Ask);
        require(_orderId != bytes32(0));
        require(_sharesFilled <= _order.sharesEscrowed);
        require(_tokensFilled <= _order.moneyEscrowed);
        require(_order.price <= _order.market.getMarketDenominator());
        uint256 _fill = 0;
        if (_order.tradeType == Order.TradeTypes.Bid) {
            _fill = _sharesFilled + _tokensFilled.div(_order.price);
        } else if (_order.tradeType == Order.TradeTypes.Ask) {
            _fill = _sharesFilled + _tokensFilled.div(_order.market.getMarketDenominator().sub(_order.price));
        }
        require(_fill <= _order.amount);
        _order.amount -= _fill;
        _order.moneyEscrowed -= _tokensFilled;
        _order.sharesEscrowed -= _sharesFilled;
        if (_order.amount == 0) {
            require(_order.moneyEscrowed == 0);
            require(_order.sharesEscrowed == 0);
            removeOrderFromList(_orderId);
            _order.price = 0;
            _order.maker = address(0);
            _order.betterOrderId = bytes32(0);
            _order.worseOrderId = bytes32(0);
        }
        return true;
    }

    function takeOrderLog(bytes32 _orderId, address _taker, uint256 _makerSharesFilled, uint256 _makerTokensFilled, uint256 _takerSharesFilled, uint256 _takerTokensFilled, uint256 _tradeGroupId) public constant returns (bool) {
        Order.Data storage _order = orders[_orderId];
        TakeOrder(_order.market, _order.outcome, _order.tradeType, _orderId, _order.price, _order.maker, _taker, _makerSharesFilled, _makerTokensFilled, _takerSharesFilled, _takerTokensFilled, _tradeGroupId);
        return true;
    }

    function buyCompleteSetsLog(address _sender, IMarket _market, uint256 _amount, uint256 _numOutcomes) public constant returns (bool) {
        BuyCompleteSets(_sender, _market, _amount, _numOutcomes);
        return true;
    }

    function sellCompleteSetsLog(address _sender, IMarket _market, uint256 _amount, uint256 _numOutcomes, uint256 _marketCreatorFee, uint256 _reportingFee) public constant returns (bool) {
        SellCompleteSets(_sender, _market, _amount, _numOutcomes, _marketCreatorFee, _reportingFee);
        return true;
    }

    function cancelOrderLog(bytes32 _orderId) public constant returns (bool) {
        Order.Data storage _order = orders[_orderId];
        CancelOrder(_order.market, _order.maker, _order.price, _order.amount, _orderId, _order.outcome, _order.tradeType, _order.moneyEscrowed, _order.sharesEscrowed);
        return true;
    }

    function setPrice(IMarket _market, uint8 _outcome, uint256 _price) external returns (bool) {
        marketOrderData[_market].prices[_outcome] = _price;
        return true;
    }

    function removeOrderFromList(bytes32 _orderId) private returns (bool) {
        Order.TradeTypes _type = orders[_orderId].tradeType;
        IMarket _market = orders[_orderId].market;
        uint8 _outcome = orders[_orderId].outcome;
        bytes32 _betterOrderId = orders[_orderId].betterOrderId;
        bytes32 _worseOrderId = orders[_orderId].worseOrderId;
        if (bestOrder[getBestOrderWorstOrderHash(_market, _outcome, _type)] == _orderId) {
            bestOrder[getBestOrderWorstOrderHash(_market, _outcome, _type)] = _worseOrderId;
        }
        if (worstOrder[getBestOrderWorstOrderHash(_market, _outcome, _type)] == _orderId) {
            worstOrder[getBestOrderWorstOrderHash(_market, _outcome, _type)] = _betterOrderId;
        }
        if (_betterOrderId != bytes32(0)) {
            orders[_betterOrderId].worseOrderId = _worseOrderId;
        }
        if (_worseOrderId != bytes32(0)) {
            orders[_worseOrderId].betterOrderId = _betterOrderId;
        }
        orders[_orderId].betterOrderId = bytes32(0);
        orders[_orderId].worseOrderId = bytes32(0);
        return true;
    }

    /**
     * @dev If best bid is not set or price higher than best bid price, this order is the new best bid.
     */
    function updateBestBidOrder(bytes32 _orderId, IMarket _market, uint256 _price, uint8 _outcome) private returns (bytes32) {
        bytes32 _bestBidOrderId = bestOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.TradeTypes.Bid)];
        if (_bestBidOrderId == bytes32(0) || _price > orders[_bestBidOrderId].price) {
            bestOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.TradeTypes.Bid)] = _orderId;
        }
        return bestOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.TradeTypes.Bid)];
    }

    /**
     * @dev If worst bid is not set or price lower than worst bid price, this order is the new worst bid.
     */
    function updateWorstBidOrder(bytes32 _orderId, IMarket _market, uint256 _price, uint8 _outcome) private returns (bytes32) {
        bytes32 _worstBidOrderId = worstOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.TradeTypes.Bid)];
        if (_worstBidOrderId == bytes32(0) || _price < orders[_worstBidOrderId].price) {
            worstOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.TradeTypes.Bid)] = _orderId;
        }
        return worstOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.TradeTypes.Bid)];
    }

    /**
     * @dev If best ask is not set or price lower than best ask price, this order is the new best ask.
     */
    function updateBestAskOrder(bytes32 _orderId, IMarket _market, uint256 _price, uint8 _outcome) private returns (bytes32) {
        bytes32 _bestAskOrderId = bestOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.TradeTypes.Ask)];
        if (_bestAskOrderId == bytes32(0) || _price < orders[_bestAskOrderId].price) {
            bestOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.TradeTypes.Ask)] = _orderId;
        }
        return bestOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.TradeTypes.Ask)];
    }

    /**
     * @dev If worst ask is not set or price higher than worst ask price, this order is the new worst ask.
     */
    function updateWorstAskOrder(bytes32 _orderId, IMarket _market, uint256 _price, uint8 _outcome) private returns (bytes32) {
        bytes32 _worstAskOrderId = worstOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.TradeTypes.Ask)];
        if (_worstAskOrderId == bytes32(0) || _price > orders[_worstAskOrderId].price) {
            worstOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.TradeTypes.Ask)] = _orderId;
        }
        return worstOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.TradeTypes.Ask)];
    }

    function getBestOrderWorstOrderHash(IMarket _market, uint8 _outcome, Order.TradeTypes _type) private constant returns (bytes32) {
        return sha256(_market, _outcome, _type);
    }
}
