// Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE

// Bid / Ask actions: puts orders on the book
// price is always in 10**18 fxp, so a price of 1 is 1 WEI.
// amount is the number of attoshares the order is for (either to buy or to sell). For a currency with 18 decimals [like ether] if you buy 10**18 at a price of 10**18 then that's going to buy you ONE share [10**18 units] at a cost of ONE ETH [10**18 wei]. For a currency with say 9 decimals, if you buy 10**9 at a price of 10**18 that'll also buy you ONE full unit of that currency worth of shares. If you buy 10**9 at a price of 10**17 that'll buy you POINT_ONE full units of that currency worth of shares [so it'll cost you 10**8]. If you buy 10**8 amount at a price of 10**18 you're also effectively paying POINT_ONE units of currency, this time it's just to get you 10x less shares [in other words you're paying 10x more per share].
// price is the exact price you want to buy/sell at [which may not be the cost, for example to short a binary market it'll cost 1-price, to go long it'll cost price]
// smallest order value is 10**14 WEI

pragma solidity ^0.4.13;

import 'ROOT/IController.sol';
import 'ROOT/libraries/math/SafeMathUint256.sol';
import 'ROOT/reporting/IMarket.sol';
import 'ROOT/trading/IOrders.sol';


library Order {
    using SafeMathUint256 for uint256;

    uint256 constant MIN_ORDER_VALUE = 10**14;

    enum TradeTypes {
        Bid, Ask
    }

    enum TradeDirections {
        Long, Short
    }

    struct Data {
        // Contracts
        IOrders orders;
        IMarket market;

        // Order
        bytes32 id;
        address maker;
        uint8 outcome;
        Order.TradeTypes tradeType;
        uint256 fxpAmount;
        uint256 fxpPrice;
        uint256 fxpSharesEscrowed;
        uint256 fxpMoneyEscrowed;
        bytes32 betterOrderId;
        bytes32 worseOrderId;
    }

    //
    // Constructor
    //

    function create(IController _controller, address _maker, uint8 _outcome, Order.TradeTypes _type, uint256 _attoshares, uint256 _displayPrice, IMarket _market, bytes32 _betterOrderId, bytes32 _worseOrderId) internal returns (Data) {
        require(_market.getTypeName() == "Market");
        require(_outcome < _market.getNumberOfOutcomes());
        require(_displayPrice < _market.getMarketDenominator());

        IOrders _orders = IOrders(_controller.lookup("Orders"));

        return Data({
            orders: _orders,
            market: _market,
            id: 0,
            maker: _maker,
            outcome: _outcome,
            tradeType: _type,
            fxpAmount: _attoshares,
            fxpPrice: _displayPrice,
            fxpSharesEscrowed: 0,
            fxpMoneyEscrowed: 0,
            betterOrderId: _betterOrderId,
            worseOrderId: _worseOrderId
        });
    }

    //
    // "public" functions
    //

    function getOrderId(Order.Data _orderData) internal constant returns (bytes32) {
        if (_orderData.id == bytes32(0)) {
            bytes32 _orderId = _orderData.orders.getOrderId(_orderData.tradeType, _orderData.market, _orderData.fxpAmount, _orderData.fxpPrice, _orderData.maker, block.number, _orderData.outcome, _orderData.fxpMoneyEscrowed, _orderData.fxpSharesEscrowed);
            require(_orderData.orders.getAmount(_orderId) == 0);
            _orderData.id = _orderId;
        }
        return _orderData.id;
     }

    function getOrderTradingTypeFromMakerDirection(Order.TradeDirections _makerDirection) internal constant returns (Order.TradeTypes) {
        return (_makerDirection == Order.TradeDirections.Long) ? Order.TradeTypes.Bid : Order.TradeTypes.Ask;
    }

    function getOrderTradingTypeFromTakerDirection(Order.TradeDirections _takerDirection) internal constant returns (Order.TradeTypes) {
        return (_takerDirection == Order.TradeDirections.Long) ? Order.TradeTypes.Ask : Order.TradeTypes.Bid;
    }

    function escrowFunds(Order.Data _orderData) internal returns (bool) {
        if (_orderData.tradeType == Order.TradeTypes.Ask) {
            return escrowFundsForAsk(_orderData);
        } else if (_orderData.tradeType == Order.TradeTypes.Bid) {
            return escrowFundsForBid(_orderData);
        }
    }

    function saveOrder(Order.Data _orderData, uint256 _tradeGroupId) internal returns (bytes32) {
        return _orderData.orders.saveOrder(_orderData.tradeType, _orderData.market, _orderData.fxpAmount, _orderData.fxpPrice, _orderData.maker, _orderData.outcome, _orderData.fxpMoneyEscrowed, _orderData.fxpSharesEscrowed, _orderData.betterOrderId, _orderData.worseOrderId, _tradeGroupId);
    }

    //
    // Private functions
    //

    function escrowFundsForBid(Order.Data _orderData) private returns (bool) {
        uint256 _orderValueInAttotokens = SafeMathUint256.fxpMul(_orderData.fxpAmount, SafeMathUint256.sub(_orderData.market.getMarketDenominator(), uint256(_orderData.fxpPrice)), 1 ether);
        require(_orderValueInAttotokens >= MIN_ORDER_VALUE);

        require(_orderData.fxpMoneyEscrowed == 0);
        require(_orderData.fxpSharesEscrowed == 0);
        uint256 _attosharesToCover = _orderData.fxpAmount;
        uint8 _numberOfOutcomes = _orderData.market.getNumberOfOutcomes();

        // Figure out how many almost-complete-sets (just missing `outcome` share) the maker has
        uint256 _attosharesHeld = 2**254;
        for (uint8 _i = 0; _i < _numberOfOutcomes; _i++) {
            if (_i != _orderData.outcome) {
                uint256 _makerShareTokenBalance = _orderData.market.getShareToken(_i).balanceOf(_orderData.maker);
                _attosharesHeld = SafeMathUint256.min(_makerShareTokenBalance, _attosharesHeld);
            }
        }

        // Take shares into escrow if they have any almost-complete-sets
        if (_attosharesHeld > 0) {
            _orderData.fxpSharesEscrowed = SafeMathUint256.min(_attosharesHeld, _attosharesToCover);
            _attosharesToCover -= _orderData.fxpSharesEscrowed;
            for (_i = 0; _i < _numberOfOutcomes; _i++) {
                if (_i != _orderData.outcome) {
                    _orderData.market.getShareToken(_i).transferFrom(_orderData.maker, _orderData.market, _orderData.fxpSharesEscrowed);
                }
            }
        }
        // If not able to cover entire order with shares alone, then cover remaining with tokens
        if (_attosharesToCover > 0) {
            _orderData.fxpMoneyEscrowed = SafeMathUint256.fxpMul(_attosharesToCover, uint256(_orderData.fxpPrice), 1 ether);
            require(_orderData.market.getDenominationToken().transferFrom(_orderData.maker, _orderData.market, _orderData.fxpMoneyEscrowed));
        }

        return true;
    }

    function escrowFundsForAsk(Order.Data _orderData) private returns (bool) {
        uint256 _orderValueInAttotokens = SafeMathUint256.fxpMul(_orderData.fxpAmount, uint256(_orderData.fxpPrice), 1 ether);
        require(_orderValueInAttotokens >= MIN_ORDER_VALUE);

        require(_orderData.fxpMoneyEscrowed == 0);
        require(_orderData.fxpSharesEscrowed == 0);
        IShareToken _shareToken = _orderData.market.getShareToken(_orderData.outcome);
        uint256 _attosharesToCover = _orderData.fxpAmount;

        // Figure out how many shares of the outcome the maker has
        uint256 _attosharesHeld = _shareToken.balanceOf(_orderData.maker);

        // Take shares in escrow if user has shares
        if (_attosharesHeld > 0) {
            _orderData.fxpSharesEscrowed = SafeMathUint256.min(_attosharesHeld, _attosharesToCover);
            _attosharesToCover -= _orderData.fxpSharesEscrowed;
            _shareToken.transferFrom(_orderData.maker, _orderData.market, _orderData.fxpSharesEscrowed);
        }

        // If not able to cover entire order with shares alone, then cover remaining with tokens
        if (_attosharesToCover > 0) {
            _orderData.fxpMoneyEscrowed = SafeMathUint256.fxpMul(_attosharesToCover, SafeMathUint256.sub(_orderData.market.getMarketDenominator(), uint256(_orderData.fxpPrice)), 1 ether);
            require(_orderData.market.getDenominationToken().transferFrom(_orderData.maker, _orderData.market, _orderData.fxpMoneyEscrowed));
        }

        return true;
    }
}
