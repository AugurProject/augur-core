pragma solidity 0.4.20;


import 'trading/ITradingEscapeHatch.sol';
import 'trading/ICash.sol';
import 'trading/IOrders.sol';
import 'trading/IShareToken.sol';
import 'libraries/CashAutoConverter.sol';
import 'libraries/DelegationTarget.sol';
import 'libraries/MarketValidator.sol';
import 'libraries/math/SafeMathUint256.sol';


contract TradingEscapeHatch is DelegationTarget, CashAutoConverter, MarketValidator, ITradingEscapeHatch {
    using SafeMathUint256 for uint256;

    // market => (outcome => frozenShareValue)
    mapping(address => mapping(uint256 => uint256)) private frozenShareValues;

    function claimSharesInUpdate(IMarket _market) public marketIsLegit(_market) convertToAndFromCash onlyInBadTimes returns(bool) {
        ICash _marketCurrency = _market.getDenominationToken();
        uint256 _amountToTransfer = getFrozenShareValueInMarketAndDeleteShares(_market);
        require(_marketCurrency.transferFrom(_market, msg.sender, _amountToTransfer));
        return true;
    }

    function getFrozenShareValueInMarket(IMarket _market) public onlyInBadTimes returns (uint256) {
        uint256 _numOutcomes = _market.getNumberOfOutcomes();
        uint256 _frozenShareValueInMarket = 0;

        for (uint256 _outcome = 0; _outcome < _numOutcomes; ++_outcome) {
            IShareToken _shareToken = _market.getShareToken(_outcome);
            uint256 _sharesOwned = _shareToken.balanceOf(msg.sender);
            if (_sharesOwned > 0) {
                uint256 _frozenShareValue = getFrozenShareValue(_market, _numOutcomes, _outcome);
                _frozenShareValueInMarket += _sharesOwned.mul(_frozenShareValue);
            }
        }
        return _frozenShareValueInMarket;
    }

    function getFrozenShareValueInMarketAndDeleteShares(IMarket _market) private onlyInBadTimes returns (uint256) {
        uint256 _numOutcomes = _market.getNumberOfOutcomes();
        uint256 _frozenShareValueInMarket = 0;

        for (uint256 _outcome = 0; _outcome < _numOutcomes; ++_outcome) {
            IShareToken _shareToken = _market.getShareToken(_outcome);
            uint256 _sharesOwned = _shareToken.balanceOf(msg.sender);
            if (_sharesOwned > 0) {
                uint256 _frozenShareValue = getFrozenShareValue(_market, _numOutcomes, _outcome);
                _shareToken.destroyShares(msg.sender, _sharesOwned);
                _frozenShareValueInMarket += _sharesOwned.mul(_frozenShareValue);
            }
        }
        return _frozenShareValueInMarket;
    }

    function getFrozenShareValue(IMarket _market, uint256 _numOutcomes, uint256 _outcome) internal returns(uint256) {
        require(_outcome < _numOutcomes);

        if (frozenShareValues[_market][_outcome] != 0) {
            return frozenShareValues[_market][_outcome];
        }

        memoizeFrozenShareValues(_market, _numOutcomes);
        return frozenShareValues[_market][_outcome];
    }

    function memoizeFrozenShareValues(IMarket _market, uint256 _numOutcomes) internal {
        uint256 _numberOfMissingBids = 0;
        uint256[] memory _shiftedPrices = new uint256[](_numOutcomes);
        uint256 _sumOfBids = 0;
        IOrders _orders = IOrders(controller.lookup("Orders"));

        // fill in any outcome prices that have an order history
        for (uint256 _tempOutcome = 0; _tempOutcome < _numOutcomes; ++_tempOutcome) {
            uint256 _lastTradePrice = uint256(_orders.getLastOutcomePrice(_market, _tempOutcome));
            uint256 _lastTradePriceShifted = _lastTradePrice;
            if (_lastTradePriceShifted > 0) {
                _shiftedPrices[_tempOutcome] = _lastTradePriceShifted;
                _sumOfBids += _lastTradePriceShifted;
            } else {
                _numberOfMissingBids += 1;
            }
        }

        // fill in any outcome prices that have no order history
        if (_numberOfMissingBids > 0) {
            // Leaving the redundant / here for stack depth issues
            uint256 _fauxBidPrice = (_market.getNumTicks().sub(_sumOfBids)) / _numberOfMissingBids;
            // to avoid any oddities, every share is worth _something_, even if it is just 1 attotoken
            if (_fauxBidPrice == 0) {
                _fauxBidPrice = 1;
            }
            for (_tempOutcome = 0; _tempOutcome < _numOutcomes; ++_tempOutcome) {
                if (_shiftedPrices[_tempOutcome] == 0) {
                    _shiftedPrices[_tempOutcome] = _fauxBidPrice;
                    _sumOfBids += _fauxBidPrice;
                }
            }
        }

        // set the final prices to be what should be paid out to each outcome share holder
        for (_tempOutcome = 0; _tempOutcome < _numOutcomes; ++_tempOutcome) {
            // The market denominator will have to be < ~10**26 or a single complete set would be unpurchaseable with the total supply of ETH, so there is no realistic risk of overflow here in any case where shares actually exist in the market
            frozenShareValues[_market][_tempOutcome] = _shiftedPrices[_tempOutcome].mul(_market.getNumTicks()).div(_sumOfBids);
        }
    }
}
