pragma solidity 0.4.18;


import 'trading/IFillOrder.sol';
import 'Augur.sol';
import 'Controlled.sol';
import 'libraries/ReentrancyGuard.sol';
import 'libraries/math/SafeMathUint256.sol';
import 'reporting/IMarket.sol';
import 'trading/ICash.sol';
import 'trading/ICompleteSets.sol';
import 'trading/IOrders.sol';
import 'trading/IShareToken.sol';
import 'trading/Order.sol';
import 'libraries/CashAutoConverter.sol';
import 'libraries/Extractable.sol';


// CONSIDER: At some point it would probably be a good idea to shift much of the logic from trading contracts into extensions. In particular this means sorting for making and WCL calculcations + order walking for taking.
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
        Augur augur;
    }

    struct FilledOrder {
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
        FilledOrder order;
        Participant creator;
        Participant filler;
    }

    //
    // Constructor
    //

    function create(IController _controller, bytes32 _orderId, address _fillerAddress, uint256 _fillerSize) internal view returns (Data) {
        // TODO: data validation

        Contracts memory _contracts = getContracts(_controller, _orderId);
        FilledOrder memory _order = getOrder(_contracts, _orderId);
        Order.Types _orderOrderType = _contracts.orders.getOrderType(_orderId);
        Participant memory _creator = getMaker(_contracts, _order, _orderOrderType);
        Participant memory _filler = getFiller(_contracts, _orderOrderType, _fillerAddress, _fillerSize);

        return Data({
            contracts: _contracts,
            order: _order,
            creator: _creator,
            filler: _filler
        });
    }

    //
    // "public" functions
    //

    function tradeMakerSharesForFillerShares(Data _data) internal returns (uint256, uint256) {
        uint256 _numberOfCompleteSets = _data.creator.sharesToSell.min(_data.filler.sharesToSell);
        if (_numberOfCompleteSets == 0) {
            return (0, 0);
        }

        // transfer shares to this contract from each participant
        _data.contracts.longShareToken.trustedFillOrderTransfer(getLongShareSellerSource(_data), this, _numberOfCompleteSets);
        for (uint8 _i = 0; _i < _data.contracts.shortShareTokens.length; ++_i) {
            _data.contracts.shortShareTokens[_i].trustedFillOrderTransfer(getShortShareSellerSource(_data), this, _numberOfCompleteSets);
        }

        // sell complete sets
        var (_marketCreatorFees, _reporterFees) = _data.contracts.completeSets.sellCompleteSets(this, _data.contracts.market, _numberOfCompleteSets);

        // distribute payout proportionately (fees will have been deducted)
        uint256 _payout = _data.contracts.denominationToken.balanceOf(this);
        uint256 _longShare = _payout.mul(_data.order.sharePriceLong).div(_data.order.sharePriceRange);
        uint256 _shortShare = _payout.sub(_longShare);
        _data.contracts.denominationToken.transfer(getLongShareSellerDestination(_data), _longShare);
        _data.contracts.denominationToken.transfer(getShortShareSellerDestination(_data), _shortShare);

        // update available shares for creator and filler
        _data.creator.sharesToSell -= _numberOfCompleteSets;
        _data.filler.sharesToSell -= _numberOfCompleteSets;
        return (_marketCreatorFees, _reporterFees);
    }

    function tradeMakerSharesForFillerTokens(Data _data) internal returns (bool) {
        uint256 _numberOfSharesToTrade = _data.creator.sharesToSell.min(_data.filler.sharesToBuy);
        if (_numberOfSharesToTrade == 0) {
            return true;
        }

        // transfer shares from creator (escrowed in market) to filler
        if (_data.creator.direction == Direction.Short) {
            _data.contracts.longShareToken.trustedFillOrderTransfer(_data.contracts.market, _data.filler.participantAddress, _numberOfSharesToTrade);
        } else {
            for (uint8 _i = 0; _i < _data.contracts.shortShareTokens.length; ++_i) {
                _data.contracts.shortShareTokens[_i].trustedFillOrderTransfer(_data.contracts.market, _data.filler.participantAddress, _numberOfSharesToTrade);
            }
        }

        uint256 _tokensToCover = getTokensToCover(_data, _data.filler.direction, _numberOfSharesToTrade);
        _data.contracts.augur.trustedTransfer(_data.contracts.denominationToken, _data.filler.participantAddress, _data.creator.participantAddress, _tokensToCover);

        // update available assets for creator and filler
        _data.creator.sharesToSell -= _numberOfSharesToTrade;
        _data.filler.sharesToBuy -= _numberOfSharesToTrade;
        return true;
    }

    function tradeMakerTokensForFillerShares(Data _data) internal returns (bool) {
        uint256 _numberOfSharesToTrade = _data.filler.sharesToSell.min(_data.creator.sharesToBuy);
        if (_numberOfSharesToTrade == 0) {
            return true;
        }

        // transfer shares from filler to creator
        if (_data.filler.direction == Direction.Short) {
            _data.contracts.longShareToken.trustedFillOrderTransfer(_data.filler.participantAddress, _data.creator.participantAddress, _numberOfSharesToTrade);
        } else {
            for (uint8 _i = 0; _i < _data.contracts.shortShareTokens.length; ++_i) {
                _data.contracts.shortShareTokens[_i].trustedFillOrderTransfer(_data.filler.participantAddress, _data.creator.participantAddress, _numberOfSharesToTrade);
            }
        }

        // transfer tokens from creator (escrowed in market) to filler
        uint256 _tokensToCover = getTokensToCover(_data, _data.creator.direction, _numberOfSharesToTrade);
        _data.contracts.denominationToken.transferFrom(_data.contracts.market, _data.filler.participantAddress, _tokensToCover);

        // update available assets for creator and filler
        _data.creator.sharesToBuy -= _numberOfSharesToTrade;
        _data.filler.sharesToSell -= _numberOfSharesToTrade;
        return true;
    }

    function tradeMakerTokensForFillerTokens(Data _data) internal returns (bool) {
        uint256 _numberOfCompleteSets = _data.creator.sharesToBuy.min(_data.filler.sharesToBuy);
        if (_numberOfCompleteSets == 0) {
            return true;
        }

        // transfer tokens to this contract
        uint256 _creatorTokensToCover = getTokensToCover(_data, _data.creator.direction, _numberOfCompleteSets);
        uint256 _fillerTokensToCover = getTokensToCover(_data, _data.filler.direction, _numberOfCompleteSets);

        _data.contracts.denominationToken.transferFrom(_data.contracts.market, this, _creatorTokensToCover);
        _data.contracts.augur.trustedTransfer(_data.contracts.denominationToken, _data.filler.participantAddress, this, _fillerTokensToCover);

        // buy complete sets
        uint256 _cost = _numberOfCompleteSets.mul(_data.contracts.market.getNumTicks());
        if (_data.contracts.denominationToken.allowance(this, _data.contracts.augur) < _cost) {
            _data.contracts.denominationToken.approve(_data.contracts.augur, _cost);
        }
        _data.contracts.completeSets.buyCompleteSets(this, _data.contracts.market, _numberOfCompleteSets);

        // distribute shares to participants
        address _longBuyer = getLongShareBuyerDestination(_data);
        address _shortBuyer = getShortShareBuyerDestination(_data);
        _data.contracts.longShareToken.transfer(_longBuyer, _numberOfCompleteSets);
        for (uint8 _i = 0; _i < _data.contracts.shortShareTokens.length; ++_i) {
            _data.contracts.shortShareTokens[_i].transfer(_shortBuyer, _numberOfCompleteSets);
        }

        _data.creator.sharesToBuy -= _numberOfCompleteSets;
        _data.filler.sharesToBuy -= _numberOfCompleteSets;
        return true;
    }

    //
    // Helpers
    //

    function getLongShareBuyerSource(Data _data) internal pure returns (address) {
        return (_data.creator.direction == Direction.Long) ? _data.contracts.market : _data.filler.participantAddress;
    }

    function getShortShareBuyerSource(Data _data) internal pure returns (address) {
        return (_data.creator.direction == Direction.Short) ? _data.contracts.market : _data.filler.participantAddress;
    }

    function getLongShareBuyerDestination(Data _data) internal pure returns (address) {
        return (_data.creator.direction == Direction.Long) ? _data.creator.participantAddress : _data.filler.participantAddress;
    }

    function getShortShareBuyerDestination(Data _data) internal pure returns (address) {
        return (_data.creator.direction == Direction.Short) ? _data.creator.participantAddress : _data.filler.participantAddress;
    }

    function getLongShareSellerSource(Data _data) internal pure returns (address) {
        return (_data.creator.direction == Direction.Short) ? _data.contracts.market : _data.filler.participantAddress;
    }

    function getShortShareSellerSource(Data _data) internal pure returns (address) {
        return (_data.creator.direction == Direction.Long) ? _data.contracts.market : _data.filler.participantAddress;
    }

    function getLongShareSellerDestination(Data _data) internal pure returns (address) {
        return (_data.creator.direction == Direction.Short) ? _data.creator.participantAddress : _data.filler.participantAddress;
    }

    function getShortShareSellerDestination(Data _data) internal pure returns (address) {
        return (_data.creator.direction == Direction.Long) ? _data.creator.participantAddress : _data.filler.participantAddress;
    }

    function getMakerSharesDepleted(Data _data) internal pure returns (uint256) {
        return _data.creator.startingSharesToSell.sub(_data.creator.sharesToSell);
    }

    function getFillerSharesDepleted(Data _data) internal pure returns (uint256) {
        return _data.filler.startingSharesToSell.sub(_data.filler.sharesToSell);
    }

    function getMakerTokensDepleted(Data _data) internal pure returns (uint256) {
        return getTokensDepleted(_data, _data.creator.direction, _data.creator.startingSharesToBuy, _data.creator.sharesToBuy);
    }

    function getFillerTokensDepleted(Data _data) internal pure returns (uint256) {
        return getTokensDepleted(_data, _data.filler.direction, _data.filler.startingSharesToBuy, _data.filler.sharesToBuy);
    }

    function getTokensDepleted(Data _data, Direction _direction, uint256 _startingSharesToBuy, uint256 _endingSharesToBuy) internal pure returns (uint256) {
        return _startingSharesToBuy
            .sub(_endingSharesToBuy)
            .mul((_direction == Direction.Long) ? _data.order.sharePriceLong : _data.order.sharePriceShort);
    }

    function getTokensToCover(Data _data, Direction _direction, uint256 _numShares) internal pure returns (uint256) {
        return getTokensToCover(_direction, _data.order.sharePriceLong, _data.order.sharePriceShort, _numShares);
    }

    //
    // Construction helpers
    //

    function getContracts(IController _controller, bytes32 _orderId) private view returns (Contracts memory) {
        IOrders _orders = IOrders(_controller.lookup("Orders"));
        IMarket _market = _orders.getMarket(_orderId);
        uint8 _outcome = _orders.getOutcome(_orderId);
        return Contracts({
            orders: _orders,
            market: _market,
            completeSets: ICompleteSets(_controller.lookup("CompleteSets")),
            denominationToken: _market.getDenominationToken(),
            longShareToken: _market.getShareToken(_outcome),
            shortShareTokens: getShortShareTokens(_market, _outcome),
            augur: Augur(_controller.lookup("Augur"))
        });
    }

    function getOrder(Contracts _contracts, bytes32 _orderId) private view returns (FilledOrder memory) {
        var (_sharePriceRange, _sharePriceLong, _sharePriceShort) = getSharePriceDetails(_contracts.market, _contracts.orders, _orderId);
        return FilledOrder({
            orderId: _orderId,
            outcome: _contracts.orders.getOutcome(_orderId),
            sharePriceRange: _sharePriceRange,
            sharePriceLong: _sharePriceLong,
            sharePriceShort: _sharePriceShort
        });
    }

    function getMaker(Contracts _contracts, FilledOrder _order, Order.Types _orderOrderType) private view returns (Participant memory) {
        Direction _direction = (_orderOrderType == Order.Types.Bid) ? Direction.Long : Direction.Short;
        uint256 _sharesToSell = _contracts.orders.getOrderSharesEscrowed(_order.orderId);
        uint256 _sharesToBuy = _contracts.orders.getAmount(_order.orderId).sub(_sharesToSell);
        return Participant({
            participantAddress: _contracts.orders.getOrderCreator(_order.orderId),
            direction: _direction,
            startingSharesToSell: _sharesToSell,
            startingSharesToBuy: _sharesToBuy,
            sharesToSell: _sharesToSell,
            sharesToBuy: _sharesToBuy
        });
    }

    function getFiller(Contracts _contracts, Order.Types _orderOrderType, address _address, uint256 _size) private view returns (Participant memory) {
        Direction _direction = (_orderOrderType == Order.Types.Bid) ? Direction.Short : Direction.Long;
        uint256 _sharesToSell = getFillerSharesToSell(_contracts.longShareToken, _contracts.shortShareTokens, _address, _direction, _size);
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

    function getTokensToCover(Direction _direction, uint256 _sharePriceLong, uint256 _sharePriceShort, uint256 _numShares) internal pure returns (uint256) {
        return _numShares.mul((_direction == Direction.Long) ? _sharePriceLong : _sharePriceShort);
    }

    function getShortShareTokens(IMarket _market, uint8 _longOutcome) private view returns (IShareToken[] memory) {
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

    function getSharePriceDetails(IMarket _market, IOrders _orders, bytes32 _orderId) private view returns (uint256 _sharePriceRange, uint256 _sharePriceLong, uint256 _sharePriceShort) {
        uint256 _numTicks = _market.getNumTicks();
        uint256 _orderPrice = _orders.getPrice(_orderId);
        _sharePriceShort = uint256(_numTicks - _orderPrice);
        return (_numTicks, _orderPrice, _sharePriceShort);
    }

    function getDirections(IOrders _orders, bytes32 _orderId) private view returns (Direction _creatorDirection, Direction _fillerDirection) {
        return (_orders.getOrderType(_orderId) == Order.Types.Bid)
            ? (Direction.Long, Direction.Short)
            : (Direction.Short, Direction.Long);
    }

    function getFillerSharesToSell(IShareToken _longShareToken, IShareToken[] memory _shortShareTokens, address _filler, Direction _fillerDirection, uint256 _fillerSize) private view returns (uint256) {
        uint256 _sharesAvailable = SafeMathUint256.getUint256Max();
        if (_fillerDirection == Direction.Short) {
            _sharesAvailable = _longShareToken.balanceOf(_filler);
        } else {
            for (uint8 _outcome = 0; _outcome < _shortShareTokens.length; ++_outcome) {
                _sharesAvailable = _shortShareTokens[_outcome].balanceOf(_filler).min(_sharesAvailable);
            }
        }
        return _sharesAvailable.min(_fillerSize);
    }
}


library DirectionExtensions {
    function toOrderType(Trade.Direction _direction) internal pure returns (Order.Types) {
        if (_direction == Trade.Direction.Long) {
            return Order.Types.Bid;
        } else {
            return Order.Types.Ask;
        }
    }
}


contract FillOrder is CashAutoConverter, Extractable, ReentrancyGuard, IFillOrder {
    using SafeMathUint256 for uint256;
    using Trade for Trade.Data;
    using DirectionExtensions for Trade.Direction;

    // CONSIDER: Do we want the API to be in terms of shares as it is now, or would the desired amount of ETH to place be preferable? Would both be useful?
    function publicFillOrder(bytes32 _orderId, uint256 _amountFillerWants, bytes32 _tradeGroupId) external payable convertToAndFromCash onlyInGoodTimes nonReentrant returns (uint256) {
        return this.fillOrder(msg.sender, _orderId, _amountFillerWants, _tradeGroupId);
    }

    function fillOrder(address _filler, bytes32 _orderId, uint256 _amountFillerWants, bytes32 _tradeGroupId) external onlyWhitelistedCallers returns (uint256) {
        Trade.Data memory _tradeData = Trade.create(controller, _orderId, _filler, _amountFillerWants);
        var (_marketCreatorFees, _reporterFees) = _tradeData.tradeMakerSharesForFillerShares();
        _tradeData.tradeMakerSharesForFillerTokens();
        _tradeData.tradeMakerTokensForFillerShares();
        _tradeData.tradeMakerTokensForFillerTokens();
        // Turn any remaining Cash balance the creator has into ETH. This is done for the filler though the use of a CashAutoConverter modifier
        uint256 _creatorCashBalance = _tradeData.contracts.denominationToken.balanceOf(_tradeData.creator.participantAddress);
        if (_creatorCashBalance > 0) {
            _tradeData.contracts.augur.trustedTransfer(_tradeData.contracts.denominationToken, _tradeData.creator.participantAddress, this, _creatorCashBalance);
            _tradeData.contracts.denominationToken.withdrawEtherTo(_tradeData.creator.participantAddress, _creatorCashBalance);
        }

        // AUDIT: is there a reentry risk here?  we execute all of the above code, which includes transferring tokens around, before we mark the order as filled
        logOrderFilled(_tradeData, _marketCreatorFees, _reporterFees, _tradeGroupId);
        _tradeData.contracts.orders.fillOrder(_orderId, _tradeData.getMakerSharesDepleted(), _tradeData.getMakerTokensDepleted());
        return _tradeData.filler.sharesToSell.add(_tradeData.filler.sharesToBuy);
    }

    function logOrderFilled(Trade.Data _tradeData, uint256 _marketCreatorFees, uint256 _reporterFees, bytes32 _tradeGroupId) private returns (bool) {
        controller.getAugur().logOrderFilled(_tradeData.contracts.market.getUniverse(), _tradeData.contracts.market.getShareToken(_tradeData.order.outcome), _tradeData.filler.participantAddress, _tradeData.order.orderId, _tradeData.getMakerSharesDepleted(), _tradeData.getMakerTokensDepleted(), _tradeData.getFillerSharesDepleted(), _tradeData.getFillerTokensDepleted(), _marketCreatorFees, _reporterFees, _tradeGroupId);
        return true;
    }

    function getProtectedTokens() internal returns (address[] memory) {
        return new address[](0);
    }
}
