pragma solidity ^0.4.17;

import 'trading/ICompleteSets.sol';
import 'Augur.sol';
import 'Controlled.sol';
import 'libraries/ReentrancyGuard.sol';
import 'libraries/math/SafeMathUint256.sol';
import 'trading/ICash.sol';
import 'extensions/MarketFeeCalculator.sol';
import 'reporting/IMarket.sol';
import 'reporting/IReportingWindow.sol';
import 'trading/IOrders.sol';
import 'libraries/CashAutoConverter.sol';


contract CompleteSets is Controlled, CashAutoConverter, ReentrancyGuard, ICompleteSets {
    using SafeMathUint256 for uint256;

    /**
     * Buys `_amount` shares of every outcome in the specified market.
    **/
    function publicBuyCompleteSets(IMarket _market, uint256 _amount) external payable convertToAndFromCash onlyInGoodTimes nonReentrant returns (bool) {
        return this.buyCompleteSets(msg.sender, _market, _amount);
    }

    function buyCompleteSets(address _sender, IMarket _market, uint256 _amount) external onlyWhitelistedCallers returns (bool) {
        require(_sender != address(0));
        require(_market != IMarket(0));

        uint8 _numOutcomes = _market.getNumberOfOutcomes();
        ICash _denominationToken = _market.getDenominationToken();
        Augur _augur = Augur(controller.lookup("Augur"));

        uint256 _cost = _amount.mul(_market.getNumTicks());
        require(_augur.trustedTransfer(_denominationToken, _sender, _market, _cost));
        for (uint8 _outcome = 0; _outcome < _numOutcomes; ++_outcome) {
            _market.getShareToken(_outcome).createShares(_sender, _amount);
        }

        _market.getUniverse().incrementOpenInterest(_cost);

        IOrders(controller.lookup("Orders")).buyCompleteSetsLog(_sender, _market, _amount, _numOutcomes);
        return true;
    }

    function publicSellCompleteSets(IMarket _market, uint256 _amount) external convertToAndFromCash onlyInGoodTimes nonReentrant returns (bool) {
        return this.sellCompleteSets(msg.sender, _market, _amount);
    }

    function sellCompleteSets(address _sender, IMarket _market, uint256 _amount) external onlyWhitelistedCallers returns (bool) {
        require(_sender != address(0));
        require(_market != IMarket(0));

        uint8 _numOutcomes = _market.getNumberOfOutcomes();
        ICash _denominationToken = _market.getDenominationToken();
        uint256 _creatorFeeRate = _market.getMarketCreatorSettlementFeeInAttoethPerEth();
        uint256 _payout = _amount.mul(_market.getNumTicks());
        _market.getUniverse().decrementOpenInterest(_payout);
        uint256 _creatorFee = _payout.mul(_creatorFeeRate).div(1 ether);
        IReportingWindow _reportingWindow = _market.getReportingWindow();
        uint256 _reportingFeeRate = MarketFeeCalculator(controller.lookup("MarketFeeCalculator")).getReportingFeeInAttoethPerEth(_reportingWindow);
        uint256 _reportingFee = _payout.mul(_reportingFeeRate).div(1 ether);
        _payout = _payout.sub(_creatorFee).sub(_reportingFee);

        // Takes shares away from participant and decreases the amount issued in the market since we're exchanging complete sets
        for (uint8 _outcome = 0; _outcome < _numOutcomes; ++_outcome) {
            _market.getShareToken(_outcome).destroyShares(_sender, _amount);
        }

        if (_creatorFee != 0) {
            // For this payout we transfer Cash to this contract and then convert it into ETH before giving it ot the market owner
            require(_denominationToken.transferFrom(_market, this, _creatorFee));
            _denominationToken.withdrawEtherTo(_market.getOwner(), _creatorFee);
        }
        if (_reportingFee != 0) {
            require(_denominationToken.transferFrom(_market, _reportingWindow, _reportingFee));
        }
        require(_denominationToken.transferFrom(_market, _sender, _payout));

        IOrders(controller.lookup("Orders")).sellCompleteSetsLog(_sender, _market, _amount, _numOutcomes, _creatorFee, _reportingFee);
        return true;
    }
}
