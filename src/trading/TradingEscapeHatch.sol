pragma solidity ^0.4.13;

import 'ROOT/trading/ITradingEscapeHatch.sol';
import 'ROOT/trading/ICash.sol';
import 'ROOT/trading/IOrders.sol';
import 'ROOT/trading/IShareToken.sol';
import 'ROOT/libraries/DelegationTarget.sol';
import 'ROOT/libraries/math/SafeMathUint256.sol';


contract TradingEscapeHatch is DelegationTarget, ITradingEscapeHatch {
    using SafeMathUint256 for uint256;

    // market => (outcome => frozenShareValue)
    mapping(address => mapping(uint8 => uint256)) private frozenShareValues;

    function claimSharesInUpdate(IMarket _market) public onlyInBadTimes returns(bool) {
        require(address(_market) != address(0));

        uint8 _numOutcomes = _market.getNumberOfOutcomes();
        ICash _marketCurrency = _market.getDenominationToken();

        for (uint8 _outcome = 0; _outcome < _numOutcomes; ++_outcome) {
            IShareToken _shareToken = _market.getShareToken(_outcome);
            uint256 _sharesOwned = _shareToken.balanceOf(msg.sender);
            if (_sharesOwned > 0) {
                uint256 _frozenShareValue = getFrozenShareValue(_market, _numOutcomes, _outcome);
                _shareToken.destroyShares(msg.sender, _sharesOwned);
                uint256 _amountToTransfer = _sharesOwned.mul(_frozenShareValue);
                require(_marketCurrency.transferFrom(_market, msg.sender, _amountToTransfer));
            }
        }
        return true;
    }

    function getFrozenShareValue(IMarket _market, uint8 _numOutcomes, uint8 _outcome) internal returns(uint256) {
        require(_outcome < _numOutcomes);

        if (frozenShareValues[_market][_outcome] != 0) {
            return frozenShareValues[_market][_outcome];
        }

        memoizeFrozenShareValues(_market, _numOutcomes);
        return frozenShareValues[_market][_outcome];
    }

    function memoizeFrozenShareValues(IMarket _market, uint8 _numOutcomes) internal {
        uint256 _numberOfMissingBids = 0;
        uint256[] memory _shiftedPrices = new uint256[](_numOutcomes);
        uint256 _sumOfBids = 0;
        IOrders _orders = IOrders(controller.lookup("Orders"));

        // fill in any outcome prices that have an order history
        for (uint8 _tempOutcome = 0; _tempOutcome < _numOutcomes; ++_tempOutcome) {
            uint256 _lastTradePrice = uint256(_orders.getLastOutcomePrice(_market, _tempOutcome));
            // intentionally not a safeSub since minValue may be negative
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
            uint256 _fauxBidPrice = (_market.getMarketDenominator() - _sumOfBids) / _numberOfMissingBids;
            // to avoid any oddities, every share is worth _something_, even if it is just 1 attotoken
            if (_fauxBidPrice == 0)
                _fauxBidPrice = 1;
            for (_tempOutcome = 0; _tempOutcome < _numOutcomes; ++_tempOutcome) {
                if (_shiftedPrices[_tempOutcome] == 0) {
                    _shiftedPrices[_tempOutcome] = _fauxBidPrice;
                    _sumOfBids += _fauxBidPrice;
                }
            }
        }

        // set the final prices to be what should be paid out to each outcome share holder
        for (_tempOutcome = 0; _tempOutcome < _numOutcomes; ++_tempOutcome) {
            // FIXME: Think about this math, can shiftedPrice * range be greater than 2*254?
            //        Can shiftedPrice / _sumOfBids lead to rounding errors?  Should we * then / or / then *?
            //        Yes it can be greater, shifted / _sumOfBids will lead to rounding errors
            frozenShareValues[_market][_tempOutcome] = _shiftedPrices[_tempOutcome].mul(_market.getMarketDenominator()).div(_sumOfBids);
        }
    }
}
