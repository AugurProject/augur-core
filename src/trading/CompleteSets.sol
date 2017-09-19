pragma solidity ^0.4.13;

import 'ROOT/trading/ICompleteSets.sol';
import 'ROOT/Controlled.sol';
import 'ROOT/libraries/ReentrancyGuard.sol';
import 'ROOT/libraries/math/SafeMathUint256.sol';
import 'ROOT/libraries/token/ERC20.sol';
import 'ROOT/extensions/MarketFeeCalculator.sol';
import 'ROOT/reporting/IMarket.sol';
import 'ROOT/reporting/IReportingWindow.sol';
import 'ROOT/trading/IOrders.sol';


contract CompleteSets is Controlled, ReentrancyGuard, ICompleteSets {
    using SafeMathUint256 for uint256;

    /**
     * Buys `_amount` shares of every outcome in the specified market.
    **/
    function publicBuyCompleteSets(IMarket _market, uint256 _amount) external onlyInGoodTimes nonReentrant returns (bool) {
        return this.buyCompleteSets(msg.sender, _market, _amount);
    }

    function buyCompleteSets(address _sender, IMarket _market, uint256 _amount) external onlyWhitelistedCallers returns (bool) {
        require(_sender != address(0));
        require(_market != IMarket(0));

        uint8 _numOutcomes = _market.getNumberOfOutcomes();
        ERC20 _denominationToken = _market.getDenominationToken();

        uint256 _cost = _amount.mul(_market.getMarketDenominator());
        require(_denominationToken.transferFrom(_sender, _market, _cost));
        for (uint8 _outcome = 0; _outcome < _numOutcomes; ++_outcome) {
            _market.getShareToken(_outcome).createShares(_sender, _amount);
        }

        IOrders(controller.lookup("Orders")).buyCompleteSetsLog(_sender, _market, _amount, _numOutcomes);
        return true;
    }

    function publicSellCompleteSets(IMarket _market, uint256 _amount) external onlyInGoodTimes nonReentrant returns (bool) {
        return this.sellCompleteSets(msg.sender, _market, _amount);
    }

    function sellCompleteSets(address _sender, IMarket _market, uint256 _amount) external onlyWhitelistedCallers returns (bool) {
        require(_sender != address(0));
        require(_market != IMarket(0));

        uint8 _numOutcomes = _market.getNumberOfOutcomes();
        ERC20 _denominationToken = _market.getDenominationToken();
        uint256 _marketCreatorFeeRate = _market.getMarketCreatorSettlementFeeInAttoethPerEth();
        uint256 _payout = _amount.mul(_market.getMarketDenominator());
        uint256 _marketCreatorFee = _payout.mul(_marketCreatorFeeRate).div(1 ether);
        IReportingWindow _reportingWindow = _market.getReportingWindow();
        uint256 _reportingFeeRate = MarketFeeCalculator(controller.lookup("MarketFeeCalculator")).getReportingFeeInAttoethPerEth(_reportingWindow);
        uint256 _reportingFee = _payout.mul(_reportingFeeRate).div(1 ether);
        _payout = _payout.sub(_marketCreatorFee).sub(_reportingFee);

        // Takes shares away from participant and decreases the amount issued in the market since we're exchanging complete sets
        for (uint8 _outcome = 0; _outcome < _numOutcomes; ++_outcome) {
            _market.getShareToken(_outcome).destroyShares(_sender, _amount);
        }

        if (_marketCreatorFee != 0) {
            require(_denominationToken.transferFrom(_market, _market.getOwner(), _marketCreatorFee));
        }
        if (_reportingFee != 0) {
            require(_denominationToken.transferFrom(_market, _reportingWindow, _reportingFee));
        }
        require(_denominationToken.transferFrom(_market, _sender, _payout));

        IOrders(controller.lookup("Orders")).sellCompleteSetsLog(_sender, _market, _amount, _numOutcomes, _marketCreatorFee, _reportingFee);
        return true;
    }
}
