pragma solidity 0.4.18;


import 'trading/IClaimTradingProceeds.sol';
import 'Controlled.sol';
import 'libraries/ReentrancyGuard.sol';
import 'libraries/CashAutoConverter.sol';
import 'reporting/IMarket.sol';
import 'trading/ICash.sol';
import 'libraries/math/SafeMathUint256.sol';
import 'reporting/Reporting.sol';
import 'Augur.sol';
import 'libraries/Extractable.sol';


// AUDIT: Ensure that a malicious market can't subversively cause share tokens to be paid out incorrectly.
/**
 * @title ClaimTradingProceeds
 * @dev This allows users to claim their money from a market by exchanging their shares
 */
contract ClaimTradingProceeds is CashAutoConverter, Extractable, ReentrancyGuard, IClaimTradingProceeds {
    using SafeMathUint256 for uint256;

    function claimTradingProceeds(IMarket _market) convertToAndFromCash onlyInGoodTimes nonReentrant external returns(bool) {
        if (!_market.isFinalized()) {
            _market.finalize();
        }

        require(controller.getTimestamp() > _market.getFinalizationTime() + Reporting.getClaimTradingProceedsWaitTime());

        ICash _denominationToken = _market.getDenominationToken();

        for (uint8 _outcome = 0; _outcome < _market.getNumberOfOutcomes(); ++_outcome) {
            IShareToken _shareToken = _market.getShareToken(_outcome);
            uint256 _numberOfShares = _shareToken.balanceOf(msg.sender);
            var (_proceeds, _shareHolderShare, _creatorShare, _reporterShare) = divideUpWinnings(_market, _outcome, _numberOfShares);

            if (_proceeds > 0) {
                _market.getUniverse().decrementOpenInterest(_proceeds);
            }

            // always destroy shares as it gives a minor gas refund and is good for the network
            if (_numberOfShares > 0) {
                _shareToken.destroyShares(msg.sender, _numberOfShares);
                logTradingProceedsClaimed(_market, _shareToken, msg.sender, _numberOfShares, _shareHolderShare);
            }
            if (_shareHolderShare > 0) {
                require(_denominationToken.transferFrom(_market, msg.sender, _shareHolderShare));
            }
            if (_creatorShare > 0) {
                require(_denominationToken.transferFrom(_market, _market.getMarketCreatorMailbox(), _creatorShare));
            }
            if (_reporterShare > 0) {
                require(_denominationToken.transferFrom(_market, _market.getUniverse().getOrCreateNextFeeWindow(), _reporterShare));
            }
        }

        return true;
    }

    function logTradingProceedsClaimed(IMarket _market, address _shareToken, address _sender, uint256 _numShares, uint256 _numPayoutTokens) private returns (bool) {
        controller.getAugur().logTradingProceedsClaimed(_market.getUniverse(), _shareToken, _sender, _market, _numShares, _numPayoutTokens, _sender.balance.add(_numPayoutTokens));
    }

    function divideUpWinnings(IMarket _market, uint8 _outcome, uint256 _numberOfShares) public returns (uint256 _proceeds, uint256 _shareHolderShare, uint256 _creatorShare, uint256 _reporterShare) {
        _proceeds = calculateProceeds(_market, _outcome, _numberOfShares);
        _creatorShare = calculateCreatorFee(_market, _proceeds);
        _reporterShare = calculateReportingFee(_market, _proceeds);
        _shareHolderShare = _proceeds.sub(_creatorShare).sub(_reporterShare);
        return (_proceeds, _shareHolderShare, _creatorShare, _reporterShare);
    }

    function calculateProceeds(IMarket _market, uint8 _outcome, uint256 _numberOfShares) public view returns (uint256) {
        uint256 _payoutNumerator = _market.getWinningPayoutNumerator(_outcome);
        return _numberOfShares.mul(_payoutNumerator);
    }

    function calculateReportingFee(IMarket _market, uint256 _amount) public returns (uint256) {
        uint256 _reportingFeeDivisor = _market.getUniverse().getOrCacheReportingFeeDivisor();
        return _amount.div(_reportingFeeDivisor);
    }

    function calculateCreatorFee(IMarket _market, uint256 _amount) public view returns (uint256) {
        uint256 _creatorFeeDivisor = _market.getMarketCreatorSettlementFeeDivisor();
        return _amount.div(_creatorFeeDivisor);
    }

    function getProtectedTokens() internal returns (address[] memory) {
        return new address[](0);
    }
}
