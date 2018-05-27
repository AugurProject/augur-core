pragma solidity 0.4.20;


import 'trading/ICompleteSets.sol';
import 'IAugur.sol';
import 'Controlled.sol';
import 'libraries/ReentrancyGuard.sol';
import 'libraries/math/SafeMathUint256.sol';
import 'libraries/MarketValidator.sol';
import 'trading/ICash.sol';
import 'reporting/IMarket.sol';
import 'reporting/IFeeWindow.sol';
import 'trading/IOrders.sol';
import 'libraries/CashAutoConverter.sol';


contract CompleteSets is Controlled, CashAutoConverter, ReentrancyGuard, MarketValidator, ICompleteSets {
    using SafeMathUint256 for uint256;

    /**
     * Buys `_amount` shares of every outcome in the specified market.
    **/
    function publicBuyCompleteSets(IMarket _market, uint256 _amount) external marketIsLegit(_market) payable convertToAndFromCash onlyInGoodTimes returns (bool) {
        this.buyCompleteSets(msg.sender, _market, _amount);
        controller.getAugur().logCompleteSetsPurchased(_market.getUniverse(), _market, msg.sender, _amount);
        _market.assertBalances();
        return true;
    }

    function buyCompleteSets(address _sender, IMarket _market, uint256 _amount) external onlyWhitelistedCallers nonReentrant returns (bool) {
        require(_sender != address(0));

        uint256 _numOutcomes = _market.getNumberOfOutcomes();
        ICash _denominationToken = _market.getDenominationToken();
        IAugur _augur = controller.getAugur();

        uint256 _cost = _amount.mul(_market.getNumTicks());
        require(_augur.trustedTransfer(_denominationToken, _sender, _market, _cost));
        for (uint256 _outcome = 0; _outcome < _numOutcomes; ++_outcome) {
            _market.getShareToken(_outcome).createShares(_sender, _amount);
        }

        if (!_market.isFinalized()) {
            _market.getUniverse().incrementOpenInterest(_cost);
        }

        return true;
    }

    function publicSellCompleteSets(IMarket _market, uint256 _amount) external marketIsLegit(_market) convertToAndFromCash onlyInGoodTimes returns (bool) {
        this.sellCompleteSets(msg.sender, _market, _amount);
        controller.getAugur().logCompleteSetsSold(_market.getUniverse(), _market, msg.sender, _amount);
        _market.assertBalances();
        return true;
    }

    function sellCompleteSets(address _sender, IMarket _market, uint256 _amount) external onlyWhitelistedCallers nonReentrant returns (uint256 _creatorFee, uint256 _reportingFee) {
        require(_sender != address(0));

        uint256 _numOutcomes = _market.getNumberOfOutcomes();
        ICash _denominationToken = _market.getDenominationToken();
        uint256 _payout = _amount.mul(_market.getNumTicks());
        if (!_market.isFinalized()) {
            _market.getUniverse().decrementOpenInterest(_payout);
        }
        _creatorFee = _market.deriveMarketCreatorFeeAmount(_payout);
        uint256 _reportingFeeDivisor = _market.getUniverse().getOrCacheReportingFeeDivisor();
        _reportingFee = _payout.div(_reportingFeeDivisor);
        _payout = _payout.sub(_creatorFee).sub(_reportingFee);

        // Takes shares away from participant and decreases the amount issued in the market since we're exchanging complete sets
        for (uint256 _outcome = 0; _outcome < _numOutcomes; ++_outcome) {
            _market.getShareToken(_outcome).destroyShares(_sender, _amount);
        }

        if (_creatorFee != 0) {
            require(_denominationToken.transferFrom(_market, _market.getMarketCreatorMailbox(), _creatorFee));
        }
        if (_reportingFee != 0) {
            IFeeWindow _feeWindow = _market.getUniverse().getOrCreateNextFeeWindow();
            require(_denominationToken.transferFrom(_market, _feeWindow, _reportingFee));
        }
        require(_denominationToken.transferFrom(_market, _sender, _payout));

        return (_creatorFee, _reportingFee);
    }
}
