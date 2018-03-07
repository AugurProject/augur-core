pragma solidity 0.4.20;


import 'trading/IOrders.sol';
import 'libraries/DelegationTarget.sol';
import 'libraries/math/SafeMathUint256.sol';
import 'libraries/math/SafeMathInt256.sol';
import 'trading/Order.sol';
import 'reporting/IMarket.sol';
import 'trading/IOrdersFetcher.sol';


/**
 * @title Orders
 * @dev Storage of all data associated with orders
 */
contract Orders is DelegationTarget, IOrders {
    using Order for Order.Data;
    using SafeMathUint256 for uint256;

    struct MarketOrders {
        uint256 totalEscrowed;
        mapping(uint256 => uint256) prices;
    }

    mapping(bytes32 => Order.Data) private orders;
    mapping(address => MarketOrders) private marketOrderData;
    mapping(bytes32 => bytes32) private bestOrder;
    mapping(bytes32 => bytes32) private worstOrder;

    // Getters
    function getMarket(bytes32 _orderId) public view returns (IMarket) {
        return orders[_orderId].market;
    }

    function getOrderType(bytes32 _orderId) public view returns (Order.Types) {
        return orders[_orderId].orderType;
    }

    function getOutcome(bytes32 _orderId) public view returns (uint256) {
        return orders[_orderId].outcome;
    }

    function getAmount(bytes32 _orderId) public view returns (uint256) {
        return orders[_orderId].amount;
    }

    function getPrice(bytes32 _orderId) public view returns (uint256) {
        return orders[_orderId].price;
    }

    function getOrderCreator(bytes32 _orderId) public view returns (address) {
        return orders[_orderId].creator;
    }

    function getOrderSharesEscrowed(bytes32 _orderId) public view returns (uint256) {
        return orders[_orderId].sharesEscrowed;
    }

    function getOrderMoneyEscrowed(bytes32 _orderId) public view returns (uint256) {
        return orders[_orderId].moneyEscrowed;
    }

    function getTotalEscrowed(IMarket _market) public view returns (uint256) {
        return marketOrderData[_market].totalEscrowed;
    }

    function getLastOutcomePrice(IMarket _market, uint256 _outcome) public view returns (uint256) {
        return marketOrderData[_market].prices[_outcome];
    }

    function getBetterOrderId(bytes32 _orderId) public view returns (bytes32) {
        return orders[_orderId].betterOrderId;
    }

    function getWorseOrderId(bytes32 _orderId) public view returns (bytes32) {
        return orders[_orderId].worseOrderId;
    }

    function getBestOrderId(Order.Types _type, IMarket _market, uint256 _outcome) public view returns (bytes32) {
        return bestOrder[getBestOrderWorstOrderHash(_market, _outcome, _type)];
    }

    function getWorstOrderId(Order.Types _type, IMarket _market, uint256 _outcome) public view returns (bytes32) {
        return worstOrder[getBestOrderWorstOrderHash(_market, _outcome, _type)];
    }

    function getOrderId(Order.Types _type, IMarket _market, uint256 _amount, uint256 _price, address _sender, uint256 _blockNumber, uint256 _outcome, uint256 _moneyEscrowed, uint256 _sharesEscrowed) public pure returns (bytes32) {
        return sha256(_type, _market, _amount, _price, _sender, _blockNumber, _outcome, _moneyEscrowed, _sharesEscrowed);
    }

    function isBetterPrice(Order.Types _type, uint256 _price, bytes32 _orderId) public view returns (bool) {
        if (_type == Order.Types.Bid) {
            return (_price > orders[_orderId].price);
        } else if (_type == Order.Types.Ask) {
            return (_price < orders[_orderId].price);
        }
    }

    function isWorsePrice(Order.Types _type, uint256 _price, bytes32 _orderId) public view returns (bool) {
        if (_type == Order.Types.Bid) {
            return (_price < orders[_orderId].price);
        } else {
            return (_price > orders[_orderId].price);
        }
    }

    function assertIsNotBetterPrice(Order.Types _type, uint256 _price, bytes32 _betterOrderId) public view returns (bool) {
        require(!isBetterPrice(_type, _price, _betterOrderId));
        return true;
    }

    function assertIsNotWorsePrice(Order.Types _type, uint256 _price, bytes32 _worseOrderId) public returns (bool) {
        require(!isWorsePrice(_type, _price, _worseOrderId));
        return true;
    }

    function insertOrderIntoList(Order.Data storage _order, bytes32 _betterOrderId, bytes32 _worseOrderId) private returns (bool) {
        bytes32 _bestOrderId = bestOrder[getBestOrderWorstOrderHash(_order.market, _order.outcome, _order.orderType)];
        bytes32 _worstOrderId = worstOrder[getBestOrderWorstOrderHash(_order.market, _order.outcome, _order.orderType)];
        IOrdersFetcher _ordersFetcher = IOrdersFetcher(controller.lookup("OrdersFetcher"));
        (_betterOrderId, _worseOrderId) = _ordersFetcher.findBoundingOrders(_order.orderType, _order.price, _bestOrderId, _worstOrderId, _betterOrderId, _worseOrderId);
        if (_order.orderType == Order.Types.Bid) {
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

    function saveOrder(Order.Types _type, IMarket _market, uint256 _amount, uint256 _price, address _sender, uint256 _outcome, uint256 _moneyEscrowed, uint256 _sharesEscrowed, bytes32 _betterOrderId, bytes32 _worseOrderId, bytes32 _tradeGroupId) public onlyWhitelistedCallers returns (bytes32 _orderId) {
        require(_outcome < _market.getNumberOfOutcomes());
        _orderId = getOrderId(_type, _market, _amount, _price, _sender, block.number, _outcome, _moneyEscrowed, _sharesEscrowed);
        Order.Data storage _order = orders[_orderId];
        _order.orders = this;
        _order.market = _market;
        _order.id = _orderId;
        _order.orderType = _type;
        _order.outcome = _outcome;
        _order.price = _price;
        _order.amount = _amount;
        _order.creator = _sender;
        _order.moneyEscrowed = _moneyEscrowed;
        _order.orders.incrementTotalEscrowed(_market, _moneyEscrowed);
        _order.sharesEscrowed = _sharesEscrowed;
        insertOrderIntoList(_order, _betterOrderId, _worseOrderId);
        controller.getAugur().logOrderCreated(_type, _amount, _price, _sender, _moneyEscrowed, _sharesEscrowed, _tradeGroupId, _orderId, _order.market.getUniverse(), _order.market.getShareToken(_order.outcome));
        return _orderId;
    }

    function removeOrder(bytes32 _orderId) public onlyWhitelistedCallers returns (bool) {
        removeOrderFromList(_orderId);
        delete orders[_orderId];
        return true;
    }

    function recordFillOrder(bytes32 _orderId, uint256 _sharesFilled, uint256 _tokensFilled) public onlyWhitelistedCallers returns (bool) {
        Order.Data storage _order = orders[_orderId];
        require(_order.outcome < _order.market.getNumberOfOutcomes());
        require(_orderId != bytes32(0));
        require(_sharesFilled <= _order.sharesEscrowed);
        require(_tokensFilled <= _order.moneyEscrowed);
        require(_order.price <= _order.market.getNumTicks());
        uint256 _fill = 0;
        if (_order.orderType == Order.Types.Bid) {
            _fill = _sharesFilled.add(_tokensFilled.div(_order.price));
        } else if (_order.orderType == Order.Types.Ask) {
            uint256 _fillPrice = _order.market.getNumTicks().sub(_order.price);
            _fill = _sharesFilled.add(_tokensFilled.div(_fillPrice));
        }
        require(_fill <= _order.amount);
        _order.amount -= _fill;
        _order.moneyEscrowed -= _tokensFilled;
        _order.orders.decrementTotalEscrowed(_order.market, _tokensFilled);
        _order.sharesEscrowed -= _sharesFilled;
        if (_order.amount == 0) {
            require(_order.moneyEscrowed == 0);
            require(_order.sharesEscrowed == 0);
            removeOrderFromList(_orderId);
            _order.price = 0;
            _order.creator = address(0);
            _order.betterOrderId = bytes32(0);
            _order.worseOrderId = bytes32(0);
        }
        return true;
    }

    function setPrice(IMarket _market, uint256 _outcome, uint256 _price) external onlyWhitelistedCallers returns (bool) {
        marketOrderData[_market].prices[_outcome] = _price;
        return true;
    }

    function incrementTotalEscrowed(IMarket _market, uint256 _amount) external onlyWhitelistedCallers returns (bool) {
        marketOrderData[_market].totalEscrowed += _amount;
        return true;
    }

    function decrementTotalEscrowed(IMarket _market, uint256 _amount) external onlyWhitelistedCallers returns (bool) {
        marketOrderData[_market].totalEscrowed -= _amount;
        return true;
    }

    function removeOrderFromList(bytes32 _orderId) private returns (bool) {
        Order.Types _type = orders[_orderId].orderType;
        IMarket _market = orders[_orderId].market;
        uint256 _outcome = orders[_orderId].outcome;
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
    function updateBestBidOrder(bytes32 _orderId, IMarket _market, uint256 _price, uint256 _outcome) private returns (bytes32) {
        bytes32 _bestBidOrderId = bestOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.Types.Bid)];
        if (_bestBidOrderId == bytes32(0) || _price > orders[_bestBidOrderId].price) {
            bestOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.Types.Bid)] = _orderId;
        }
        return bestOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.Types.Bid)];
    }

    /**
     * @dev If worst bid is not set or price lower than worst bid price, this order is the new worst bid.
     */
    function updateWorstBidOrder(bytes32 _orderId, IMarket _market, uint256 _price, uint256 _outcome) private returns (bytes32) {
        bytes32 _worstBidOrderId = worstOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.Types.Bid)];
        if (_worstBidOrderId == bytes32(0) || _price < orders[_worstBidOrderId].price) {
            worstOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.Types.Bid)] = _orderId;
        }
        return worstOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.Types.Bid)];
    }

    /**
     * @dev If best ask is not set or price lower than best ask price, this order is the new best ask.
     */
    function updateBestAskOrder(bytes32 _orderId, IMarket _market, uint256 _price, uint256 _outcome) private returns (bytes32) {
        bytes32 _bestAskOrderId = bestOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.Types.Ask)];
        if (_bestAskOrderId == bytes32(0) || _price < orders[_bestAskOrderId].price) {
            bestOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.Types.Ask)] = _orderId;
        }
        return bestOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.Types.Ask)];
    }

    /**
     * @dev If worst ask is not set or price higher than worst ask price, this order is the new worst ask.
     */
    function updateWorstAskOrder(bytes32 _orderId, IMarket _market, uint256 _price, uint256 _outcome) private returns (bytes32) {
        bytes32 _worstAskOrderId = worstOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.Types.Ask)];
        if (_worstAskOrderId == bytes32(0) || _price > orders[_worstAskOrderId].price) {
            worstOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.Types.Ask)] = _orderId;
        }
        return worstOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.Types.Ask)];
    }

    function getBestOrderWorstOrderHash(IMarket _market, uint256 _outcome, Order.Types _type) private pure returns (bytes32) {
        return sha256(_market, _outcome, _type);
    }
}
