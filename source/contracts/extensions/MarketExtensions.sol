pragma solidity ^0.4.13;

import 'reporting/IReportingWindow.sol';
import 'reporting/IMarket.sol';
import 'reporting/IDisputeBond.sol';
import 'reporting/Reporting.sol';


/**
 * @title MarketExtensions
 * @dev functions moved from the market contract into a library to reduce the size of the market contract under the EVM limit
 */
contract MarketExtensions {
    function getWinningPayoutDistributionHashFromFork(IMarket _market) public constant returns (bytes32) {
        IReportingWindow _reportingWindow = _market.getReportingWindow();
        if (_reportingWindow.getUniverse().getForkingMarket() != _market) {
            return 0;
        }
        IReputationToken _winningDestination = _reportingWindow.getReputationToken().getTopMigrationDestination();
        if (address(_winningDestination) == address(0)) {
            return 0;
        }
        uint256 _halfTotalSupply = 11 * 10**6 * 10**18 / 2;
        if (_winningDestination.totalSupply() < _halfTotalSupply && block.timestamp < _reportingWindow.getUniverse().getForkEndTime()) {
            return 0;
        }
        return _winningDestination.getUniverse().getParentPayoutDistributionHash();
    }

    function getOrderedWinningPayoutDistributionHashes(IMarket _market, bytes32 _payoutDistributionHash) public returns (bytes32, bytes32) {
        bytes32 _tentativeWinningPayoutDistributionHash = _market.getTentativeWinningPayoutDistributionHash();
        bytes32 _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash = _market.getBestGuessSecondPlaceTentativeWinningPayoutDistributionHash();
        int256 _tentativeWinningStake = getPayoutDistributionHashStake(_market, _tentativeWinningPayoutDistributionHash);
        int256 _secondPlaceStake = getPayoutDistributionHashStake(_market, _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash);
        int256 _payoutStake = getPayoutDistributionHashStake(_market, _payoutDistributionHash);

        if (_tentativeWinningStake >= _secondPlaceStake && _secondPlaceStake >= _payoutStake) {
            _tentativeWinningPayoutDistributionHash = (_tentativeWinningStake > 0) ? _tentativeWinningPayoutDistributionHash: bytes32(0);
            _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash = (_secondPlaceStake > 0) ? _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash : bytes32(0);
        } else if (_tentativeWinningStake >= _payoutStake && _payoutStake >= _secondPlaceStake) {
            _tentativeWinningPayoutDistributionHash = (_tentativeWinningStake > 0) ? _tentativeWinningPayoutDistributionHash: bytes32(0);
            _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash = (_payoutStake > 0) ? _payoutDistributionHash : bytes32(0);
        } else if (_secondPlaceStake >= _tentativeWinningStake && _tentativeWinningStake >= _payoutStake) {
            _tentativeWinningPayoutDistributionHash = (_secondPlaceStake > 0) ? _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash: bytes32(0);
            _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash = (_tentativeWinningStake > 0) ? _tentativeWinningPayoutDistributionHash: bytes32(0);
        } else if (_secondPlaceStake >= _payoutStake && _payoutStake >= _tentativeWinningStake) {
            _tentativeWinningPayoutDistributionHash = (_secondPlaceStake > 0) ? _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash: bytes32(0);
            _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash = (_payoutStake > 0) ? _payoutDistributionHash: bytes32(0);
        } else if (_payoutStake >= _tentativeWinningStake && _tentativeWinningStake >= _secondPlaceStake) {
            _tentativeWinningPayoutDistributionHash = (_payoutStake > 0) ? _payoutDistributionHash: bytes32(0);
            _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash = (_tentativeWinningStake > 0) ? _tentativeWinningPayoutDistributionHash: bytes32(0);
        } else if (_payoutStake >= _secondPlaceStake && _secondPlaceStake >= _tentativeWinningStake) {
            _tentativeWinningPayoutDistributionHash = (_payoutStake > 0) ? _payoutDistributionHash: bytes32(0);
            _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash = (_secondPlaceStake > 0) ? _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash: bytes32(0);
        }

        return (_tentativeWinningPayoutDistributionHash, _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash);
    }

    function getPayoutDistributionHashStake(IMarket _market, bytes32 _payoutDistributionHash) public constant returns (int256) {
        if (_payoutDistributionHash == bytes32(0)) {
            return 0;
        }

        IReportingToken _reportingToken = _market.getReportingTokenOrZeroByPayoutDistributionHash(_payoutDistributionHash);
        if (address(_reportingToken) == address(0)) {
            return 0;
        }

        int256 _payoutStake = int256(_reportingToken.totalSupply());

        IDisputeBond _designatedDisputeBond = _market.getDesignatedReporterDisputeBondToken();
        IDisputeBond _limitedDisputeBond = _market.getLimitedReportersDisputeBondToken();
        IDisputeBond _allDisputeBond = _market.getAllReportersDisputeBondToken();

        if (address(_designatedDisputeBond) != address(0)) {
            if (_designatedDisputeBond.getDisputedPayoutDistributionHash() == _payoutDistributionHash) {
                _payoutStake -= int256(Reporting.designatedReporterDisputeBondAmount());
            }
        }
        if (address(_limitedDisputeBond) != address(0)) {
            if (_limitedDisputeBond.getDisputedPayoutDistributionHash() == _payoutDistributionHash) {
                _payoutStake -= int256(Reporting.limitedReportersDisputeBondAmount());
            }
        }
        if (address(_allDisputeBond) != address(0)) {
            if (_allDisputeBond.getDisputedPayoutDistributionHash() == _payoutDistributionHash) {
                _payoutStake -= int256(Reporting.allReportersDisputeBondAmount());
            }
        }

        return _payoutStake;
    }

    function getMarketReportingState(IMarket _market) public constant returns (IMarket.ReportingState) {
        // This market has been finalized
        if (_market.getFinalPayoutDistributionHash() != bytes32(0)) {
            return IMarket.ReportingState.FINALIZED;
        }

        // If there is an active fork we need to migrate
        IMarket _forkingMarket = _market.getForkingMarket();
        if (address(_forkingMarket) != address(0) && _forkingMarket != _market) {
            return IMarket.ReportingState.AWAITING_FORK_MIGRATION;
        }

        // Before trading in the market is finished
        if (block.timestamp < _market.getEndTime()) {
            return IMarket.ReportingState.PRE_REPORTING;
        }

        // Designated reporting period has not passed yet
        if (block.timestamp < _market.getDesignatedReportDueTimestamp()) {
            return IMarket.ReportingState.DESIGNATED_REPORTING;
        }

        bool _designatedReportDisputed = address(_market.getDesignatedReporterDisputeBondToken()) != address(0);
        bool _limitedReportDisputed = address(_market.getLimitedReportersDisputeBondToken()) != address(0);

        // If we have a designated report that hasn't been disputed it is either in the dispute window or we can finalize the market
        if (_market.getDesignatedReportReceivedTime() != 0 && !_designatedReportDisputed) {
            bool _beforeDesignatedDisputeDue = block.timestamp < _market.getDesignatedReportDisputeDueTimestamp();
            return _beforeDesignatedDisputeDue ? IMarket.ReportingState.DESIGNATED_DISPUTE : IMarket.ReportingState.AWAITING_FINALIZATION;
        }

        // If this market is the one forking we are in the process of migration or we're ready to finalize
        if (_forkingMarket == _market) {
            if (getWinningPayoutDistributionHashFromFork(_market) != bytes32(0)) {
                return IMarket.ReportingState.AWAITING_FINALIZATION;
            }
            return IMarket.ReportingState.FORKING;
        }

        IReportingWindow _reportingWindow = _market.getReportingWindow();
        bool _reportingWindowOver = block.timestamp > _reportingWindow.getEndTime();

        if (_reportingWindowOver) {
            if (_market.getTentativeWinningPayoutDistributionHash() == bytes32(0)) {
                return IMarket.ReportingState.AWAITING_NO_REPORT_MIGRATION;
            }
            return IMarket.ReportingState.AWAITING_FINALIZATION;
        }

        // If a limited dispute bond has been posted we are in some phase of all reporting depending on time
        if (_limitedReportDisputed) {
            if (_reportingWindow.isDisputeActive()) {
                if (_market.getTentativeWinningPayoutDistributionHash() == bytes32(0)) {
                    return IMarket.ReportingState.AWAITING_NO_REPORT_MIGRATION;
                } else {
                    return IMarket.ReportingState.ALL_DISPUTE;
                }
            }
            return IMarket.ReportingState.ALL_REPORTING;
        }

        // Either no designated report was made or the designated report was disputed so we are in some phase of limited reporting
        if (_reportingWindow.isDisputeActive()) {
            if (_market.getTentativeWinningPayoutDistributionHash() == bytes32(0)) {
                return IMarket.ReportingState.AWAITING_NO_REPORT_MIGRATION;
            } else {
                return IMarket.ReportingState.LIMITED_DISPUTE;
            }
        }

        return IMarket.ReportingState.LIMITED_REPORTING;
    }
}
