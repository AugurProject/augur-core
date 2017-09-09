pragma solidity ^0.4.13;

import 'ROOT/trading/IOrders.sol';
import 'ROOT/libraries/DelegationTarget.sol';
import 'ROOT/libraries/math/SafeMathUint256.sol';
import 'ROOT/libraries/trading/Order.sol';
import 'ROOT/reporting/IMarket.sol';
import 'ROOT/trading/IOrdersFetcher.sol';


/**
 * @title Orders
 * @dev Storage of all data associated with orders
 */
contract Orders is DelegationTarget, IOrders {
    using Order for Order.Data;
    using SafeMathUint256 for uint256;

    event CancelOrder(address indexed market, address indexed sender, int256 fxpPrice, uint256 fxpAmount, bytes32 orderId, uint8 outcome, Order.TradeTypes orderType, uint256 cashRefund, uint256 sharesRefund);
    event BuyCompleteSets(address indexed sender, address indexed market, uint256 fxpAmount, uint256 numOutcomes);
    event SellCompleteSets(address indexed sender, address indexed market, uint256 fxpAmount, uint256 numOutcomes, uint256 marketCreatorFee, uint256 reportingFee);
    event MakeOrder(address indexed market, address indexed sender, Order.TradeTypes indexed orderType, int256 fxpPrice, uint256 fxpAmount, uint8 outcome, bytes32 orderId, uint256 fxpMoneyEscrowed, uint256 fxpSharesEscrowed, uint256 tradeGroupId);
    event TakeOrder(address indexed market, uint8 indexed outcome, Order.TradeTypes indexed orderType, bytes32 orderId, int256 price, address maker, address taker, uint256 makerShares, int256 makerTokens, uint256 takerShares, int256 takerTokens, uint256 tradeGroupId);

    struct MarketOrders {
        uint256 volume;
        mapping(uint8 => int256) prices;
    }

    mapping(bytes32 => Order.Data) private orders;
    mapping(address => MarketOrders) private marketOrderData;
    mapping(bytes32 => bytes32) private bestOrder;
    mapping(bytes32 => bytes32) private worstOrder;

    // Getters
    // this function doesn't work because delegated contracts can't return tuples or dynamic arrays
    function getOrders(bytes32 _orderId) public constant returns (uint256 _amount, int256 _displayPrice, address _owner, uint256 _sharesEscrowed, uint256 _tokensEscrowed, bytes32 _betterOrderId, bytes32 _worseOrderId) {
        Order.Data storage _order = orders[_orderId];
        return (_order.fxpAmount, _order.fxpPrice, _order.maker, _order.fxpSharesEscrowed, _order.fxpMoneyEscrowed, _order.betterOrderId, _order.worseOrderId);
    }

    function getBestOrders(Order.TradeTypes _type, IMarket _market, uint8 _outcome) public constant returns (bytes32) {
        return bestOrder[getBestOrderWorstOrderHash(_market, _outcome, _type)];
    }

    function getWorstOrders(Order.TradeTypes _type, IMarket _market, uint8 _outcome) public constant returns (bytes32) {
        return worstOrder[getBestOrderWorstOrderHash(_market, _outcome, _type)];
    }

    function getAmount(bytes32 _orderId, Order.TradeTypes, IMarket, uint8) public constant returns (uint256) {
        return orders[_orderId].fxpAmount;
    }

    function getPrice(bytes32 _orderId, Order.TradeTypes, IMarket, uint8) public constant returns (int256) {
        return orders[_orderId].fxpPrice;
    }

    function getOrderMaker(bytes32 _orderId, Order.TradeTypes, IMarket, uint8) public constant returns (address) {
        return orders[_orderId].maker;
    }

    function getOrderSharesEscrowed(bytes32 _orderId, Order.TradeTypes, IMarket, uint8) public constant returns (uint256) {
        return orders[_orderId].fxpSharesEscrowed;
    }

    function getOrderMoneyEscrowed(bytes32 _orderId, Order.TradeTypes, IMarket, uint8) public constant returns (uint256) {
        return orders[_orderId].fxpMoneyEscrowed;
    }

    function getVolume(IMarket _market) public constant returns (uint256) {
        return marketOrderData[_market].volume;
    }

    function getLastOutcomePrice(IMarket _market, uint8 _outcome) public constant returns (int256) {
        return marketOrderData[_market].prices[_outcome];
    }

    function getBetterOrderId(bytes32 _orderId, Order.TradeTypes, IMarket, uint8) public constant returns (bytes32) {
        return orders[_orderId].betterOrderId;
    }

    function getWorseOrderId(bytes32 _orderId, Order.TradeTypes, IMarket, uint8) public constant returns (bytes32) {
        return orders[_orderId].worseOrderId;
    }

    function getBestOrderId(Order.TradeTypes _type, IMarket _market, uint8 _outcome) public constant returns (bytes32) {
        return bestOrder[getBestOrderWorstOrderHash(_market, _outcome, _type)];
    }

    function getWorstOrderId(Order.TradeTypes _type, IMarket _market, uint8 _outcome) public constant returns (bytes32) {
        return worstOrder[getBestOrderWorstOrderHash(_market, _outcome, _type)];
    }

    function getOrderId(Order.TradeTypes _type, IMarket _market, uint256 _fxpAmount, int256 _fxpPrice, address _sender, uint256 _blockNumber, uint8 _outcome, uint256 _fxpMoneyEscrowed, uint256 _fxpSharesEscrowed) public constant returns (bytes32) {
        return sha256(_type, _market, _fxpAmount, _fxpPrice, _sender, _blockNumber, _outcome, _fxpMoneyEscrowed, _fxpSharesEscrowed);
    }

    function isBetterPrice(Order.TradeTypes _type, IMarket, uint8, int256 _fxpPrice, bytes32 _orderId) public constant returns (bool) {
        require(_type == Order.TradeTypes.Bid || _type == Order.TradeTypes.Ask);
        if (_type == Order.TradeTypes.Bid) {
            return (_fxpPrice > orders[_orderId].fxpPrice);
        } else if (_type == Order.TradeTypes.Ask) {
            return (_fxpPrice < orders[_orderId].fxpPrice);
        }
    }

    function isWorsePrice(Order.TradeTypes _type, IMarket, uint8, int256 _fxpPrice, bytes32 _orderId) public constant returns (bool) {
        if (_type == Order.TradeTypes.Bid) {
            return (_fxpPrice < orders[_orderId].fxpPrice);
        } else {
            return (_fxpPrice > orders[_orderId].fxpPrice);
        }
    }

    function assertIsNotBetterPrice(Order.TradeTypes _type, IMarket _market, uint8 _outcome, int256 _fxpPrice, bytes32 _betterOrderId) public constant returns (bool) {
        require(!isBetterPrice(_type, _market, _outcome, _fxpPrice, _betterOrderId));
        return true;
    }

    function assertIsNotWorsePrice(Order.TradeTypes _type, IMarket _market, uint8 _outcome, int256 _fxpPrice, bytes32 _worseOrderId) public returns (bool) {
        require(!isWorsePrice(_type, _market, _outcome, _fxpPrice, _worseOrderId));
        return true;
    }

    function insertOrderIntoList(bytes32 _orderId, Order.TradeTypes _type, IMarket _market, uint8 _outcome, int256 _fxpPrice, bytes32 _betterOrderId, bytes32 _worseOrderId) internal returns (bool) {
        bytes32 _bestOrderId = bestOrder[getBestOrderWorstOrderHash(_market, _outcome, _type)];
        bytes32 _worstOrderId = worstOrder[getBestOrderWorstOrderHash(_market, _outcome, _type)];
        IOrdersFetcher _ordersFetcher = IOrdersFetcher(controller.lookup("OrdersFetcher"));
        (_betterOrderId, _worseOrderId) = _ordersFetcher.findBoundingOrders(_type, _market, _outcome, _fxpPrice, _bestOrderId, _worstOrderId, _betterOrderId, _worseOrderId);
        if (_type == Order.TradeTypes.Bid) {
            _bestOrderId = updateBestBidOrder(_orderId, _market, _fxpPrice, _outcome);
            _worstOrderId = updateWorstBidOrder(_orderId, _market, _fxpPrice, _outcome);
        } else {
            _bestOrderId = updateBestAskOrder(_orderId, _market, _fxpPrice, _outcome);
            _worstOrderId = updateWorstAskOrder(_orderId, _market, _fxpPrice, _outcome);
        }
        if (_bestOrderId == _orderId) {
            _betterOrderId = bytes32(0);
        }
        if (_worstOrderId == _orderId) {
            _worseOrderId = bytes32(0);
        }
        if (_betterOrderId != bytes32(0)) {
            orders[_betterOrderId].worseOrderId = _orderId;
            orders[_orderId].betterOrderId = _betterOrderId;
        }
        if (_worseOrderId != bytes32(0)) {
            orders[_worseOrderId].betterOrderId = _orderId;
            orders[_orderId].worseOrderId = _worseOrderId;
        }
        return true;
    }

    function saveOrder(Order.TradeTypes _type, IMarket _market, uint256 _fxpAmount, int256 _fxpPrice, address _sender, uint8 _outcome, uint256 _fxpMoneyEscrowed, uint256 _fxpSharesEscrowed, bytes32 _betterOrderId, bytes32 _worseOrderId, uint256 _tradeGroupId) public onlyWhitelistedCallers returns (bytes32 _orderId) {
        require(_outcome < _market.getNumberOfOutcomes());
        _orderId = getOrderId(_type, _market, _fxpAmount, _fxpPrice, _sender, block.number, _outcome, _fxpMoneyEscrowed, _fxpSharesEscrowed);
        insertOrderIntoList(_orderId, _type, _market, _outcome, _fxpPrice, _betterOrderId, _worseOrderId);
        orders[_orderId].orders = this;
        orders[_orderId].market = _market;
        orders[_orderId].id = _orderId;
        orders[_orderId].fxpPrice = _fxpPrice;
        orders[_orderId].fxpAmount = _fxpAmount;
        orders[_orderId].maker = _sender;
        orders[_orderId].fxpMoneyEscrowed = _fxpMoneyEscrowed;
        orders[_orderId].fxpSharesEscrowed = _fxpSharesEscrowed;
        MakeOrder(_market, _sender, _type, _fxpPrice, _fxpAmount, _outcome, _orderId, _fxpMoneyEscrowed, _fxpSharesEscrowed, _tradeGroupId);
        return _orderId;
    }

    function removeOrder(bytes32 _orderId, Order.TradeTypes _type, IMarket _market, uint8 _outcome) public onlyWhitelistedCallers returns (bool) {
        removeOrderFromList(_orderId, _type, _market, _outcome);
        // TODO: Test replacing the lines below with `delete orders[_orderId]` to see if we can get a full gas refund.
        orders[_orderId].id = 0;
        orders[_orderId].fxpPrice = 0;
        orders[_orderId].fxpAmount = 0;
        orders[_orderId].maker = 0;
        orders[_orderId].fxpMoneyEscrowed = 0;
        orders[_orderId].fxpSharesEscrowed = 0;
        return true;
    }

    function fillOrder(bytes32 _orderId, Order.TradeTypes _orderType, IMarket _market, uint8 _orderOutcome, uint256 _sharesFilled, uint256 _tokensFilled) public onlyWhitelistedCallers returns (bool) {
        require(_market.getTypeName() == "Market");
        require(_orderOutcome < _market.getNumberOfOutcomes());
        require(_orderType == Order.TradeTypes.Bid || _orderType == Order.TradeTypes.Ask);
        require(_orderId != bytes32(0));
        require(_sharesFilled <= orders[_orderId].fxpSharesEscrowed);
        require(_tokensFilled <= orders[_orderId].fxpMoneyEscrowed);
        require(orders[_orderId].fxpPrice <= _market.getMaxDisplayPrice());
        require(orders[_orderId].fxpPrice >= _market.getMinDisplayPrice());
        require(_market.getMaxDisplayPrice() + _market.getMinDisplayPrice() <= 2**254);
        uint256 _fill = 0;
        // FIXME: We need to investigate why the fxpDiv() lines below are passing in our test scripts.  We shouldn't need to do fxpDiv(x, 10^18) since fxpDiv() is already dividing by 10^18.
        if (_orderType == Order.TradeTypes.Bid) {
            // We can't use safeSub here because it disallows subtracting negative numbers. Worst case here is an operation of 2**254 - 1 as required above, which won't overflow
            _fill = _sharesFilled + _tokensFilled.fxpDiv(uint(orders[_orderId].fxpPrice - _market.getMinDisplayPrice()), 1 ether);
        } else if (_orderType == Order.TradeTypes.Ask) {
            // We can't use safeSub here because it disallows subtracting negative numbers. Worst case here is an operation of 2**254 - 1 as required above, which won't overflow
            _fill = _sharesFilled + _tokensFilled.fxpDiv(uint(_market.getMaxDisplayPrice() - orders[_orderId].fxpPrice), 1 ether);
        }
        require(_fill <= orders[_orderId].fxpAmount);
        orders[_orderId].fxpAmount -= _fill;
        orders[_orderId].fxpMoneyEscrowed -= _tokensFilled;
        orders[_orderId].fxpSharesEscrowed -= _sharesFilled;
        if (orders[_orderId].fxpAmount == 0) {
            require(orders[_orderId].fxpMoneyEscrowed == 0);
            require(orders[_orderId].fxpSharesEscrowed == 0);
            removeOrderFromList(_orderId, _orderType, _market, _orderOutcome);
            orders[_orderId].fxpPrice = 0;
            orders[_orderId].maker = address(0);
            orders[_orderId].betterOrderId = bytes32(0);
            orders[_orderId].worseOrderId = bytes32(0);
        }
        return true;
    }

    function takeOrderLog(IMarket _market, uint8 _orderOutcome, Order.TradeTypes _orderType, bytes32 _orderId, address _taker, uint256 _makerSharesFilled, int256 _makerTokensFilled, uint256 _takerSharesFilled, int256 _takerTokensFilled, uint256 _tradeGroupId) public constant returns (bool) {
        int256 _price = orders[_orderId].fxpPrice;
        address _maker = orders[_orderId].maker;
        TakeOrder(_market, _orderOutcome, _orderType, _orderId, _price, _maker, _taker, _makerSharesFilled, _makerTokensFilled, _takerSharesFilled, _takerTokensFilled, _tradeGroupId);
        return true;
    }

    function buyCompleteSetsLog(address _sender, IMarket _market, uint256 _fxpAmount, uint256 _numOutcomes) public constant returns (bool) {
        BuyCompleteSets(_sender, _market, _fxpAmount, _numOutcomes);
        return true;
    }

    function sellCompleteSetsLog(address _sender, IMarket _market, uint256 _fxpAmount, uint256 _numOutcomes, uint256 _marketCreatorFee, uint256 _reportingFee) public constant returns (bool) {
        SellCompleteSets(_sender, _market, _fxpAmount, _numOutcomes, _marketCreatorFee, _reportingFee);
        return true;
    }

    function cancelOrderLog(IMarket _market, address _sender, int256 _fxpPrice, uint256 _fxpAmount, bytes32 _orderId, uint8 _outcome, Order.TradeTypes _type, uint256 _fxpMoneyEscrowed, uint256 _fxpSharesEscrowed) public constant returns (bool) {
        CancelOrder(_market, _sender, _fxpPrice, _fxpAmount, _orderId, _outcome, _type, _fxpMoneyEscrowed, _fxpSharesEscrowed);
        return true;
    }

    function modifyMarketVolume(IMarket _market, uint256 _fxpAmount) external returns (bool) {
        marketOrderData[_market].volume += _fxpAmount;
        _market.getBranch().getTopics().updatePopularity(_market.getTopic(), _fxpAmount);
        return true;
    }

    function setPrice(IMarket _market, uint8 _outcome, int256 _fxpPrice) external returns (bool) {
        marketOrderData[_market].prices[_outcome] = _fxpPrice;
        return true;
    }

    function removeOrderFromList(bytes32 _orderId, Order.TradeTypes _type, IMarket _market, uint8 _outcome) private returns (bool) {
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
    function updateBestBidOrder(bytes32 _orderId, IMarket _market, int256 _fxpPrice, uint8 _outcome) private returns (bytes32) {
        bytes32 _bestBidOrderId = bestOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.TradeTypes.Bid)];
        if (_bestBidOrderId == bytes32(0) || _fxpPrice > orders[_bestBidOrderId].fxpPrice) {
            bestOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.TradeTypes.Bid)] = _orderId;
        }
        return bestOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.TradeTypes.Bid)];
    }

    /**
     * @dev If worst bid is not set or price lower than worst bid price, this order is the new worst bid.
     */
    function updateWorstBidOrder(bytes32 _orderId, IMarket _market, int256 _fxpPrice, uint8 _outcome) private returns (bytes32) {
        bytes32 _worstBidOrderId = worstOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.TradeTypes.Bid)];
        if (_worstBidOrderId == bytes32(0) || _fxpPrice < orders[_worstBidOrderId].fxpPrice) {
            worstOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.TradeTypes.Bid)] = _orderId;
        }
        return worstOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.TradeTypes.Bid)];
    }

    /**
     * @dev If best ask is not set or price lower than best ask price, this order is the new best ask.
     */
    function updateBestAskOrder(bytes32 _orderId, IMarket _market, int256 _fxpPrice, uint8 _outcome) private returns (bytes32) {
        bytes32 _bestAskOrderId = bestOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.TradeTypes.Ask)];
        if (_bestAskOrderId == bytes32(0) || _fxpPrice < orders[_bestAskOrderId].fxpPrice) {
            bestOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.TradeTypes.Ask)] = _orderId;
        }
        return bestOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.TradeTypes.Ask)];
    }

    /**
     * @dev If worst ask is not set or price higher than worst ask price, this order is the new worst ask.
     */
    function updateWorstAskOrder(bytes32 _orderId, IMarket _market, int256 _fxpPrice, uint8 _outcome) private returns (bytes32) {
        bytes32 _worstAskOrderId = worstOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.TradeTypes.Ask)];
        if (_worstAskOrderId == bytes32(0) || _fxpPrice > orders[_worstAskOrderId].fxpPrice) {
            worstOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.TradeTypes.Ask)] = _orderId;
        }
        return worstOrder[getBestOrderWorstOrderHash(_market, _outcome, Order.TradeTypes.Ask)];
    }

    function getBestOrderWorstOrderHash(IMarket _market, uint8 _outcome, Order.TradeTypes _type) private constant returns (bytes32) {
        return sha256(_market, _outcome, _type);
    }
}
