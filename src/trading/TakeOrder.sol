pragma solidity ^0.4.13;

import 'ROOT/trading/ITakeOrder.sol';
import 'ROOT/Controlled.sol';
import 'ROOT/libraries/ReentrancyGuard.sol';
import 'ROOT/libraries/math/SafeMathUint256.sol';
import 'ROOT/reporting/IMarket.sol';
import 'ROOT/trading/ICash.sol';
import 'ROOT/trading/ICompleteSets.sol';
import 'ROOT/trading/IOrders.sol';
import 'ROOT/trading/IShareToken.sol';
import 'ROOT/trading/Order.sol';


library Trade {
    using SafeMathUint256 for uint256;

    enum Direction {
        Long,
        Short
    }

    struct Contracts {
        IOrders orders;
        IMarket market;
        ICompleteSets completeSets;
        ICash denominationToken;
        IShareToken longShareToken;
        IShareToken[] shortShareTokens;
    }

    // TODO: come up with a better name, or consolidate `Trade.Data` and `Order.Data`
    struct MyOrder {
        bytes32 orderId;
        uint8 outcome;
        uint256 sharePriceRange;
        uint256 sharePriceLong;
        uint256 sharePriceShort;
    }

    struct Participant {
        address participantAddress;
        Direction direction;
        uint256 startingSharesToSell;
        uint256 startingSharesToBuy;
        uint256 sharesToSell;
        uint256 sharesToBuy;
    }

    struct Data {
        Contracts contracts;
        MyOrder order;
        Participant maker;
        Participant taker;
    }

    //
    // Constructor
    //

    function create(IController _controller, bytes32 _orderId, address _takerAddress, uint256 _takerSize) internal returns (Data) {
        // TODO: data validation

        Contracts memory _contracts = getContracts(_controller, _orderId);
        MyOrder memory _order = getOrder(_contracts, _orderId);
        Order.TradeTypes _orderTradeType = _contracts.orders.getTradeType(_orderId);
        Participant memory _maker = getMaker(_contracts, _order, _orderTradeType);
        Participant memory _taker = getTaker(_contracts, _orderTradeType, _takerAddress, _takerSize);

        return Data({
            contracts: _contracts,
            order: _order,
            maker: _maker,
            taker: _taker
        });
    }

    //
    // "public" functions
    //

    function tradeMakerSharesForTakerShares(Data _data) internal returns (bool) {
        uint256 _numberOfCompleteSets = _data.maker.sharesToSell.min(_data.taker.sharesToSell);
        if (_numberOfCompleteSets == 0) {
            return true;
        }

        // transfer shares to this contract from each participant
        _data.contracts.longShareToken.transferFrom(getLongShareSellerSource(_data), this, _numberOfCompleteSets);
        for (uint8 _i = 0; _i < _data.contracts.shortShareTokens.length; ++_i) {
            _data.contracts.shortShareTokens[_i].transferFrom(getShortShareSellerSource(_data), this, _numberOfCompleteSets);
        }

        // sell complete sets
        _data.contracts.completeSets.sellCompleteSets(this, _data.contracts.market, _numberOfCompleteSets);

        // distribute payout proportionately (fees will have been deducted)
        uint256 _payout = _data.contracts.denominationToken.balanceOf(this);
        uint256 _longShare = _payout.mul(_data.order.sharePriceLong).div(_data.order.sharePriceRange);
        uint256 _shortShare = _payout.sub(_longShare);
        _data.contracts.denominationToken.transfer(getLongShareSellerDestination(_data), _longShare);
        _data.contracts.denominationToken.transfer(getShortShareSellerDestination(_data), _shortShare);

        // update available shares for maker and taker
        _data.maker.sharesToSell -= _numberOfCompleteSets;
        _data.taker.sharesToSell -= _numberOfCompleteSets;
    }

    function tradeMakerSharesForTakerTokens(Data _data) internal returns (bool) {
        uint256 _numberOfSharesToTrade = _data.maker.sharesToSell.min(_data.taker.sharesToBuy);
        if (_numberOfSharesToTrade == 0) {
            return true;
        }

        // transfer shares from maker (escrowed in market) to taker
        if (_data.maker.direction == Direction.Short) {
            _data.contracts.longShareToken.transferFrom(_data.contracts.market, _data.taker.participantAddress, _numberOfSharesToTrade);
        } else {
            for (uint8 _i = 0; _i < _data.contracts.shortShareTokens.length; ++_i) {
                _data.contracts.shortShareTokens[_i].transferFrom(_data.contracts.market, _data.taker.participantAddress, _numberOfSharesToTrade);
            }
        }

        // transfer tokens from taker to maker
        uint256 _tokensToCover = getTokensToCover(_data, _data.taker.direction, _numberOfSharesToTrade);
        _data.contracts.denominationToken.transferFrom(_data.taker.participantAddress, _data.maker.participantAddress, _tokensToCover);

        // update available assets for maker and taker
        _data.maker.sharesToSell -= _numberOfSharesToTrade;
        _data.taker.sharesToBuy -= _numberOfSharesToTrade;
    }

    function tradeMakerTokensForTakerShares(Data _data) internal returns (bool) {
        uint256 _numberOfSharesToTrade = _data.taker.sharesToSell.min(_data.maker.sharesToBuy);
        if (_numberOfSharesToTrade == 0) {
            return true;
        }

        // transfer shares from taker to maker
        if (_data.taker.direction == Direction.Short) {
            _data.contracts.longShareToken.transferFrom(_data.taker.participantAddress, _data.maker.participantAddress, _numberOfSharesToTrade);
        } else {
            for (uint8 _i = 0; _i < _data.contracts.shortShareTokens.length; ++_i) {
                _data.contracts.shortShareTokens[_i].transferFrom(_data.taker.participantAddress, _data.maker.participantAddress, _numberOfSharesToTrade);
            }
        }

        // transfer tokens from maker (escrowed in market) to taker
        uint256 _tokensToCover = getTokensToCover(_data, _data.maker.direction, _numberOfSharesToTrade);
        _data.contracts.denominationToken.transferFrom(_data.contracts.market, _data.taker.participantAddress, _tokensToCover);

        // update available assets for maker and taker
        _data.maker.sharesToBuy -= _numberOfSharesToTrade;
        _data.taker.sharesToSell -= _numberOfSharesToTrade;
    }

    function tradeMakerTokensForTakerTokens(Data _data) internal returns (bool) {
        uint256 _numberOfCompleteSets = _data.maker.sharesToBuy.min(_data.taker.sharesToBuy);
        if (_numberOfCompleteSets == 0) {
            return true;
        }

        // transfer tokens to this contract
        uint256 _makerTokensToCover = getTokensToCover(_data, _data.maker.direction, _numberOfCompleteSets);
        uint256 _takerTokensToCover = getTokensToCover(_data, _data.taker.direction, _numberOfCompleteSets);
        _data.contracts.denominationToken.transferFrom(_data.contracts.market, this, _makerTokensToCover);
        _data.contracts.denominationToken.transferFrom(_data.taker.participantAddress, this, _takerTokensToCover);

        // buy complete sets
        if (_data.contracts.denominationToken.allowance(this, _data.contracts.completeSets) < _numberOfCompleteSets) {
            _data.contracts.denominationToken.approve(_data.contracts.completeSets, _numberOfCompleteSets);
        }
        _data.contracts.completeSets.buyCompleteSets(this, _data.contracts.market, _numberOfCompleteSets);

        // distribute shares to participants
        address _longBuyer = getLongShareBuyerDestination(_data);
        address _shortBuyer = getShortShareBuyerDestination(_data);
        _data.contracts.longShareToken.transfer(_longBuyer, _numberOfCompleteSets);
        for (uint8 _i = 0; _i < _data.contracts.shortShareTokens.length; ++_i) {
            _data.contracts.shortShareTokens[_i].transfer(_shortBuyer, _numberOfCompleteSets);
        }

        // update available shares for maker and taker
        _data.maker.sharesToBuy -= _numberOfCompleteSets;
        _data.taker.sharesToBuy -= _numberOfCompleteSets;
    }

    //
    // Helpers
    //

    function getLongShareBuyerSource(Data _data) internal constant returns (address) {
        return (_data.maker.direction == Direction.Long) ? _data.contracts.market : _data.taker.participantAddress;
    }

    function getShortShareBuyerSource(Data _data) internal constant returns (address) {
        return (_data.maker.direction == Direction.Short) ? _data.contracts.market : _data.taker.participantAddress;
    }

    function getLongShareBuyerDestination(Data _data) internal constant returns (address) {
        return (_data.maker.direction == Direction.Long) ? _data.maker.participantAddress : _data.taker.participantAddress;
    }

    function getShortShareBuyerDestination(Data _data) internal constant returns (address) {
        return (_data.maker.direction == Direction.Short) ? _data.maker.participantAddress : _data.taker.participantAddress;
    }

    function getLongShareSellerSource(Data _data) internal constant returns (address) {
        return (_data.maker.direction == Direction.Short) ? _data.contracts.market : _data.taker.participantAddress;
    }

    function getShortShareSellerSource(Data _data) internal constant returns (address) {
        return (_data.maker.direction == Direction.Long) ? _data.contracts.market : _data.taker.participantAddress;
    }

    function getLongShareSellerDestination(Data _data) internal constant returns (address) {
        return (_data.maker.direction == Direction.Short) ? _data.maker.participantAddress : _data.taker.participantAddress;
    }

    function getShortShareSellerDestination(Data _data) internal constant returns (address) {
        return (_data.maker.direction == Direction.Long) ? _data.maker.participantAddress : _data.taker.participantAddress;
    }

    function getMakerSharesDepleted(Data _data) internal constant returns (uint256) {
        return _data.maker.startingSharesToSell.sub(_data.maker.sharesToSell);
    }

    function getTakerSharesDepleted(Data _data) internal constant returns (uint256) {
        return _data.taker.startingSharesToSell.sub(_data.taker.sharesToSell);
    }

    function getMakerTokensDepleted(Data _data) internal constant returns (uint256) {
        return getTokensDepleted(_data, _data.maker.direction, _data.maker.startingSharesToBuy, _data.maker.sharesToBuy);
    }

    function getTakerTokensDepleted(Data _data) internal constant returns (uint256) {
        return getTokensDepleted(_data, _data.taker.direction, _data.taker.startingSharesToBuy, _data.taker.sharesToBuy);
    }

    function getTokensDepleted(Data _data, Direction _direction, uint256 _startingSharesToBuy, uint256 _endingSharesToBuy) internal constant returns (uint256) {
        return _startingSharesToBuy
            .sub(_endingSharesToBuy)
            .mul((_direction == Direction.Long) ? _data.order.sharePriceLong : _data.order.sharePriceShort)
            .div(_data.order.sharePriceRange)
        ; // move semicolon up a line when https://github.com/duaraghav8/Solium/issues/110 is fixed
    }

    function getTokensToCover(Data _data, Direction _direction, uint256 _numShares) internal constant returns (uint256) {
        return getTokensToCover(_direction, _data.order.sharePriceRange, _data.order.sharePriceLong, _data.order.sharePriceShort, _numShares);
    }

    //
    // Construction helpers
    //

    function getContracts(IController _controller, bytes32 _orderId) private constant returns (Contracts memory) {
        IOrders _orders = IOrders(_controller.lookup("Orders"));
        IMarket _market = _orders.getMarket(_orderId);
        uint8 _outcome = _orders.getOutcome(_orderId);
        return Contracts({
            orders: _orders,
            market: _market,
            completeSets: ICompleteSets(_controller.lookup("CompleteSets")),
            denominationToken: _market.getDenominationToken(),
            longShareToken: _market.getShareToken(_outcome),
            shortShareTokens: getShortShareTokens(_market, _outcome)
        });
    }

    function getOrder(Contracts _contracts, bytes32 _orderId) private constant returns (MyOrder memory) {
        var (_sharePriceRange, _sharePriceLong, _sharePriceShort) = getSharePriceDetails(_contracts.market, _contracts.orders, _orderId);
        return MyOrder({
            orderId: _orderId,
            outcome: _contracts.orders.getOutcome(_orderId),
            sharePriceRange: _sharePriceRange,
            sharePriceLong: _sharePriceLong,
            sharePriceShort: _sharePriceShort
        });
    }

    function getMaker(Contracts _contracts, MyOrder _order, Order.TradeTypes _orderTradeType) private constant returns (Participant memory) {
        Direction _direction = (_orderTradeType == Order.TradeTypes.Bid) ? Direction.Long : Direction.Short;
        uint256 _sharesToSell = _contracts.orders.getOrderSharesEscrowed(_order.orderId);
        uint256 _sharesToBuy = _contracts.orders.getAmount(_order.orderId).sub(_sharesToSell);
        return Participant({
            participantAddress: _contracts.orders.getOrderMaker(_order.orderId),
            direction: _direction,
            startingSharesToSell: _sharesToSell,
            startingSharesToBuy: _sharesToBuy,
            sharesToSell: _sharesToSell,
            sharesToBuy: _sharesToBuy
        });
    }

    function getTaker(Contracts _contracts, Order.TradeTypes _orderTradeType, address _address, uint256 _size) private constant returns (Participant memory) {
        Direction _direction = (_orderTradeType == Order.TradeTypes.Bid) ? Direction.Short : Direction.Long;
        uint256 _sharesToSell = getTakerSharesToSell(_contracts.longShareToken, _contracts.shortShareTokens, _address, _direction, _size);
        uint256 _sharesToBuy = _size.sub(_sharesToSell);
        return Participant({
            participantAddress: _address,
            direction: _direction,
            startingSharesToSell: _sharesToSell,
            startingSharesToBuy: _sharesToBuy,
            sharesToSell: _sharesToSell,
            sharesToBuy: _sharesToBuy
        });
    }

    function getTokensToCover(Direction _direction, uint256 _sharePriceRange, uint256 _sharePriceLong, uint256 _sharePriceShort, uint256 _numShares) internal constant returns (uint256) {
        return _numShares
            .mul((_direction == Direction.Long) ? _sharePriceLong : _sharePriceShort)
            .div(_sharePriceRange)
        ; // move semicolon up a line when https://github.com/duaraghav8/Solium/issues/110 is fixed
    }

    function getShortShareTokens(IMarket _market, uint8 _longOutcome) private constant returns (IShareToken[] memory) {
        IShareToken[] memory _shortShareTokens = new IShareToken[](_market.getNumberOfOutcomes() - 1);
        for (uint8 _outcome = 0; _outcome < _shortShareTokens.length + 1; ++_outcome) {
            if (_outcome == _longOutcome) {
                continue;
            }
            uint8 _index = (_outcome < _longOutcome) ? _outcome : _outcome - 1;
            _shortShareTokens[_index] = _market.getShareToken(_outcome);
        }
        return _shortShareTokens;
    }

    function getSharePriceDetails(IMarket _market, IOrders _orders, bytes32 _orderId) private constant returns (uint256 _sharePriceRange, uint256 _sharePriceLong, uint256 _sharePriceShort) {
        uint256 _maxDisplayPrice = _market.getMarketDenominator();
        uint256 _orderDisplayPrice = _orders.getPrice(_orderId);
        _sharePriceRange = _maxDisplayPrice;
        _sharePriceLong = _orderDisplayPrice;
        _sharePriceShort = uint256(_maxDisplayPrice - _orderDisplayPrice);
        return (_sharePriceRange, _sharePriceLong, _sharePriceShort);
    }

    function getDirections(IOrders _orders, bytes32 _orderId) private constant returns (Direction _makerDirection, Direction _takerDirection) {
        return (_orders.getTradeType(_orderId) == Order.TradeTypes.Bid)
            ? (Direction.Long, Direction.Short)
            : (Direction.Short, Direction.Long)
        ; // move semicolon up a line when https://github.com/duaraghav8/Solium/issues/110 is fixed
    }

    function getTakerSharesToSell(IShareToken _longShareToken, IShareToken[] memory _shortShareTokens, address _taker, Direction _takerDirection, uint256 _takerSize) private constant returns (uint256) {
        uint256 _sharesAvailable = SafeMathUint256.maxUint256();
        if (_takerDirection == Direction.Short) {
            _sharesAvailable = _longShareToken.balanceOf(_taker);
        } else {
            for (uint8 _outcome = 0; _outcome < _shortShareTokens.length; ++_outcome) {
                _sharesAvailable = _shortShareTokens[_outcome].balanceOf(_taker).min(_sharesAvailable);
            }
        }
        return _sharesAvailable.min(_takerSize);
    }
}


library DirectionExtensions {
    function toTradeType(Trade.Direction _direction) internal constant returns (Order.TradeTypes) {
        if (_direction == Trade.Direction.Long) {
            return Order.TradeTypes.Bid;
        } else {
            return Order.TradeTypes.Ask;
        }
    }
}


contract TakeOrder is Controlled, ReentrancyGuard, ITakeOrder {
    using SafeMathUint256 for uint256;
    using Trade for Trade.Data;
    using DirectionExtensions for Trade.Direction;

    function publicTakeOrder(bytes32 _orderId, uint256 _amountTakerWants, uint256 _tradeGroupId) external onlyInGoodTimes nonReentrant returns (uint256) {
        return this.takeOrder(msg.sender, _orderId, _amountTakerWants, _tradeGroupId);
    }

    function takeOrder(address _taker, bytes32 _orderId, uint256 _amountTakerWants, uint256 _tradeGroupId) external onlyWhitelistedCallers returns (uint256) {
        Trade.Data memory _tradeData = Trade.create(controller, _orderId, _taker, _amountTakerWants);
        _tradeData.tradeMakerSharesForTakerShares();
        _tradeData.tradeMakerSharesForTakerTokens();
        _tradeData.tradeMakerTokensForTakerShares();
        _tradeData.tradeMakerTokensForTakerTokens();

        // AUDIT: is there a reentry risk here?  we execute all of the above code, which includes transferring tokens around, before we mark the order as filled
        _tradeData.contracts.orders.takeOrderLog(_tradeData.order.orderId, _tradeData.taker.participantAddress, _tradeData.getMakerSharesDepleted(), _tradeData.getMakerTokensDepleted(), _tradeData.getTakerSharesDepleted(), _tradeData.getTakerTokensDepleted(), _tradeGroupId);
        _tradeData.contracts.orders.fillOrder(_orderId, _tradeData.getMakerSharesDepleted(), _tradeData.getMakerTokensDepleted());

        return _tradeData.taker.sharesToSell.add(_tradeData.taker.sharesToBuy);
    }
}
