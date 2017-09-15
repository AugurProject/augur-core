pragma solidity ^0.4.13;

import 'ROOT/trading/IClaimProceeds.sol';
import 'ROOT/Controlled.sol';
import 'ROOT/libraries/ReentrancyGuard.sol';
import 'ROOT/reporting/IMarket.sol';
import 'ROOT/trading/ICash.sol';
import 'ROOT/extensions/MarketFeeCalculator.sol';
import 'ROOT/libraries/math/SafeMathUint256.sol';
import 'ROOT/reporting/Reporting.sol';


// AUDIT: Ensure that a malicious market can't subversively cause share tokens to be paid out incorrectly.
/**
 * @title ClaimProceeds
 * @dev This allows users to claim their money from a market by exchanging their shares
 */
contract ClaimProceeds is Controlled, ReentrancyGuard, IClaimProceeds {
    using SafeMathUint256 for uint256;

    function claimProceeds(IMarket _market) onlyInGoodTimes nonReentrant external returns(bool) {
        require(_market.getReportingState() == IMarket.ReportingState.FINALIZED);
        require(block.timestamp > _market.getFinalizationTime() + Reporting.claimProceedsWaitTime());

        IReportingToken _winningReportingToken = _market.getFinalWinningReportingToken();

        for (uint8 _outcome = 0; _outcome < _market.getNumberOfOutcomes(); ++_outcome) {
            IShareToken _shareToken = _market.getShareToken(_outcome);
            uint256 _numberOfShares = _shareToken.balanceOf(msg.sender);
            var (_shareHolderShare, _creatorShare, _reporterShare) = divideUpWinnings(_market, _winningReportingToken, _outcome, _numberOfShares);

            // always destroy shares as it gives a minor gas refund and is good for the network
            if (_numberOfShares > 0) {
                _shareToken.destroyShares(msg.sender, _numberOfShares);
            }
            ICash _denominationToken = _market.getDenominationToken();
            if (_shareHolderShare > 0) {
                require(_denominationToken.transferFrom(_market, msg.sender, _shareHolderShare));
            }
            if (_creatorShare > 0) {
                require(_denominationToken.transferFrom(_market, _market.getOwner(), _creatorShare));
            }
            if (_reporterShare > 0) {
                require(_denominationToken.transferFrom(_market, _market.getReportingWindow(), _reporterShare));
            }
        }

        return true;
    }

    function divideUpWinnings(IMarket _market, IReportingToken _winningReportingToken, uint8 _outcome, uint256 _numberOfShares) public constant returns (uint256 _shareHolderShare, uint256 _creatorShare, uint256 _reporterShare) {
        uint256 _proceeds = calculateProceeds(_market, _winningReportingToken, _outcome, _numberOfShares);
        _creatorShare = calculateMarketCreatorFee(_market, _proceeds);
        _reporterShare = calculateReportingFee(_market, _proceeds);
        _shareHolderShare = _proceeds.sub(_creatorShare).sub(_reporterShare);
        return (_shareHolderShare, _creatorShare, _reporterShare);
    }

    function calculateProceeds(IMarket _market, IReportingToken _winningReportingToken, uint8 _outcome, uint256 _numberOfShares) public constant returns (uint256) {
        uint256 _payoutNumerator = _winningReportingToken.getPayoutNumerator(_outcome);
        uint256 _marketDenominator = _market.getMarketDenominator();
        // NOTE: rounding error here will result in _very_ tiny amounts of denominationToken left in the market
        return _numberOfShares.mul(_payoutNumerator).div(_marketDenominator);
    }

    function calculateReportingFee(IMarket _market, uint256 _amount) public constant returns (uint256) {
        MarketFeeCalculator _marketFeeCalculator = MarketFeeCalculator(controller.lookup("MarketFeeCalculator"));
        IReportingWindow _reportingWindow = _market.getReportingWindow();
        uint256 _reportingFeeAttoethPerEth = _marketFeeCalculator.getReportingFeeInAttoethPerEth(_reportingWindow);
        return _amount.mul(_reportingFeeAttoethPerEth).div(1 ether);
    }

    function calculateMarketCreatorFee(IMarket _market, uint256 _amount) public constant returns (uint256) {
        uint256 _marketCreatorFeeAttoEthPerEth = _market.getMarketCreatorSettlementFeeInAttoethPerEth();
        return _amount.mul(_marketCreatorFeeAttoEthPerEth).div(1 ether);
    }
}
