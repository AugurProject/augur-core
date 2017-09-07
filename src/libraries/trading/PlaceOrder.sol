// Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE

// Bid / Ask actions: puts orders on the book
// price is always in 10**18 fxp, so a price of 1 is 1 WEI.
// amount is the number of attoshares the order is for (either to buy or to sell). For a currency with 18 decimals [like ether] if you buy 10**18 at a price of 10**18 then that's going to buy you ONE share [10**18 units] at a cost of ONE ETH [10**18 wei]. For a currency with say 9 decimals, if you buy 10**9 at a price of 10**18 that'll also buy you ONE full unit of that currency worth of shares. If you buy 10**9 at a price of 10**17 that'll buy you POINT_ONE full units of that currency worth of shares [so it'll cost you 10**8]. If you buy 10**8 amount at a price of 10**18 you're also effectively paying POINT_ONE units of currency, this time it's just to get you 10x less shares [in other words you're paying 10x more per share].
// price is the exact price you want to buy/sell at [which may not be the cost, for example to short a binary market it'll cost 1-price, to go long it'll cost price]
// smallest order value is 10**14 WEI

pragma solidity ^0.4.13;

import 'ROOT/IController.sol';
import 'ROOT/libraries/math/SafeMathUint256.sol';
import 'ROOT/trading/Trading.sol';
import 'ROOT/trading/IOrders.sol';


library PlaceOrder {
    using SafeMathUint256 for uint256;

    uint256 constant minOrderValue = 10**14;

    struct Data {
        // Contracts
        IOrders orders;
        IMarket market;

        // Order
        address sender;
        uint8 outcome;
        Trading.TradeTypes tradeType;
        uint256 attoshares;
        int256 displayPrice;
        bytes32 betterOrderId;
        bytes32 worseOrderId;
        uint256 tradeGroupId;
    }

    //
    // Constructor
    //

    function create(IController _controller, address _sender, uint8 _outcome, Trading.TradeTypes _type, uint256 _attoshares, int256 _displayPrice, IMarket _market, bytes32 _betterOrderId, bytes32 _worseOrderId, uint256 _tradeGroupId) internal returns (Data) {
        require(_market.getTypeName() == "Market");
        require(_outcome < _market.getNumberOfOutcomes());
        require(_market.getMinDisplayPrice() < _displayPrice && _displayPrice < _market.getMaxDisplayPrice());

        IOrders _orders = IOrders(_controller.lookup("Orders"));

        return Data({
            orders: _orders,
            market: _market,
            sender: _sender,
            outcome: _outcome,
            tradeType: _type,
            attoshares: _attoshares,
            displayPrice: _displayPrice,
            betterOrderId: _betterOrderId,
            worseOrderId: _worseOrderId,
            tradeGroupId: _tradeGroupId
        });
    }

    //
    // "public" functions
    //

    function placeBid(PlaceOrder.Data _data) internal returns (uint256, uint256) {
        uint256 _orderValueInAttotokens = SafeMathUint256.fxpMul(_data.attoshares, SafeMathUint256.sub(_data.market.getCompleteSetCostInAttotokens(), uint256(_data.displayPrice)), 1 ether);
        require(_orderValueInAttotokens >= minOrderValue);

        uint256 _attotokensEscrowed = 0;
        uint256 _attosharesEscrowed = 0;
        uint256 _attosharesToCover = _data.attoshares;
        uint8 _numberOfOutcomes = _data.market.getNumberOfOutcomes();

        // Figure out how many almost-complete-sets (just missing `outcome` share) the maker has
        uint256 _attosharesHeld = 2**254;
        uint8 _i = 0;
        while (_i < _numberOfOutcomes) {
            if (_i != _data.outcome) {
                uint256 _senderShareTokenBalance = _data.market.getShareToken(_i).balanceOf(_data.sender);
                _attosharesHeld = SafeMathUint256.min(_senderShareTokenBalance, _attosharesHeld);
            }
            _i += 1;
        }

        // Take shares into escrow if they have any almost-complete-sets
        if (_attosharesHeld > 0) {
            _attosharesEscrowed = SafeMathUint256.min(_attosharesHeld, _attosharesToCover);
            _attosharesToCover -= _attosharesEscrowed;
            _i = 0;
            while (_i < _numberOfOutcomes) {
                if (_i != _data.outcome) {
                    _data.market.getShareToken(_i).transferFrom(_data.sender, _data.market, _attosharesEscrowed);
                }
                _i += 1;
            }
        }
        // If not able to cover entire order with shares alone, then cover remaining with tokens
        if (_attosharesToCover > 0) {
            _attotokensEscrowed = SafeMathUint256.fxpMul(_attosharesToCover, uint256(_data.displayPrice), 1 ether);
            require(_data.market.getDenominationToken().transferFrom(_data.sender, _data.market, _attotokensEscrowed));
        }

        return (_attotokensEscrowed, _attosharesEscrowed);
    }

    function placeAsk(PlaceOrder.Data _data) internal returns (uint256, uint256) {
        uint256 _orderValueInAttotokens = SafeMathUint256.fxpMul(_data.attoshares, uint256(_data.displayPrice), 1 ether);
        require(_orderValueInAttotokens >= minOrderValue);

        uint256 _attotokensEscrowed = 0;
        uint256 _attosharesEscrowed = 0;
        IShareToken _shareToken = _data.market.getShareToken(_data.outcome);
        uint256 _attosharesToCover = _data.attoshares;

        // Figure out how many shares of the outcome the maker has
        uint256 _attosharesHeld = _shareToken.balanceOf(_data.sender);

        // Take shares in escrow if user has shares
        if (_attosharesHeld > 0) {
            _attosharesEscrowed = SafeMathUint256.min(_attosharesHeld, _attosharesToCover);
            _attosharesToCover -= _attosharesEscrowed;
            _shareToken.transferFrom(_data.sender, _data.market, _attosharesEscrowed);
        }

        // If not able to cover entire order with shares alone, then cover remaining with tokens
        if (_attosharesToCover > 0) {
            _attotokensEscrowed = SafeMathUint256.fxpMul(_attosharesToCover, SafeMathUint256.sub(_data.market.getCompleteSetCostInAttotokens(), uint256(_data.displayPrice)), 1 ether);
            require(_data.market.getDenominationToken().transferFrom(_data.sender, _data.market, _attotokensEscrowed));
        }

        return (_attotokensEscrowed, _attosharesEscrowed);
    }
}
