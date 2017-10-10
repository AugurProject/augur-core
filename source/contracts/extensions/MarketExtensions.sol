pragma solidity 0.4.17;


import 'reporting/IReportingWindow.sol';
import 'reporting/IMarket.sol';
import 'reporting/IDisputeBond.sol';
import 'reporting/Reporting.sol';


/**
 * @title MarketExtensions
 * @dev functions moved from the market contract into a library to reduce the size of the market contract under the EVM limit
 */
contract MarketExtensions {
    function getWinningPayoutDistributionHashFromFork(IMarket _market) public view returns (bytes32) {
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

    function getOrderedWinningPayoutDistributionHashes(IMarket _market, bytes32 _payoutDistributionHash) public view returns (bytes32, bytes32) {
        bytes32 _tentativeWinningPayoutDistributionHash = _market.getTentativeWinningPayoutDistributionHash();
        bytes32 _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash = _market.getBestGuessSecondPlaceTentativeWinningPayoutDistributionHash();
        if (_payoutDistributionHash == _tentativeWinningPayoutDistributionHash || _payoutDistributionHash == _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash) {
            _payoutDistributionHash = bytes32(0);
        }
        int256 _tentativeWinningStake = getPayoutDistributionHashStake(_market, _tentativeWinningPayoutDistributionHash);
        int256 _secondPlaceStake = getPayoutDistributionHashStake(_market, _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash);
        int256 _payoutStake = getPayoutDistributionHashStake(_market, _payoutDistributionHash);

        Debug(_tentativeWinningPayoutDistributionHash, _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash, _payoutDistributionHash, _tentativeWinningStake, _secondPlaceStake, _payoutStake);

        if (_tentativeWinningStake >= _secondPlaceStake && _secondPlaceStake >= _payoutStake) {
            _tentativeWinningPayoutDistributionHash = (_tentativeWinningStake > 0) ? _tentativeWinningPayoutDistributionHash: bytes32(0);
            _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash = (_secondPlaceStake > 0) ? _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash : bytes32(0);
        } else if (_tentativeWinningStake >= _payoutStake && _payoutStake >= _secondPlaceStake) {
            _tentativeWinningPayoutDistributionHash = (_tentativeWinningStake > 0) ? _tentativeWinningPayoutDistributionHash: bytes32(0);
            _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash = (_payoutStake > 0) ? _payoutDistributionHash : bytes32(0);
        } else if (_secondPlaceStake >= _tentativeWinningStake && _tentativeWinningStake >= _payoutStake) {
            _payoutDistributionHash = _tentativeWinningPayoutDistributionHash; // Reusing this as a temp value holder
            _tentativeWinningPayoutDistributionHash = (_secondPlaceStake > 0) ? _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash: bytes32(0);
            _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash = (_tentativeWinningStake > 0) ? _payoutDistributionHash: bytes32(0);
        } else if (_secondPlaceStake >= _payoutStake && _payoutStake >= _tentativeWinningStake) {
            _tentativeWinningPayoutDistributionHash = (_secondPlaceStake > 0) ? _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash: bytes32(0);
            _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash = (_payoutStake > 0) ? _payoutDistributionHash: bytes32(0);
        } else if (_payoutStake >= _tentativeWinningStake && _tentativeWinningStake >= _secondPlaceStake) {
            _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash = (_tentativeWinningStake > 0) ? _tentativeWinningPayoutDistributionHash: bytes32(0);
            _tentativeWinningPayoutDistributionHash = (_payoutStake > 0) ? _payoutDistributionHash: bytes32(0);
        } else if (_payoutStake >= _secondPlaceStake && _secondPlaceStake >= _tentativeWinningStake) {
            _tentativeWinningPayoutDistributionHash = (_payoutStake > 0) ? _payoutDistributionHash: bytes32(0);
            _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash = (_secondPlaceStake > 0) ? _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash: bytes32(0);
        }

        return (_tentativeWinningPayoutDistributionHash, _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash);
    }

    function getPayoutDistributionHashStake(IMarket _market, bytes32 _payoutDistributionHash) public view returns (int256) {
        if (_payoutDistributionHash == bytes32(0)) {
            return 0;
        }

        IReportingToken _reportingToken = _market.getReportingTokenOrZeroByPayoutDistributionHash(_payoutDistributionHash);
        if (address(_reportingToken) == address(0)) {
            return 0;
        }

        int256 _payoutStake = int256(_reportingToken.totalSupply());

        IDisputeBond _designatedDisputeBond = _market.getDesignatedReporterDisputeBondToken();
        IDisputeBond _firstDisputeBond = _market.getFirstReportersDisputeBondToken();
        IDisputeBond _lastDisputeBond = _market.getLastReportersDisputeBondToken();

        if (address(_designatedDisputeBond) != address(0)) {
            if (_designatedDisputeBond.getDisputedPayoutDistributionHash() == _payoutDistributionHash) {
                _payoutStake -= int256(Reporting.designatedReporterDisputeBondAmount());
            }
        }
        if (address(_firstDisputeBond) != address(0)) {
            if (_firstDisputeBond.getDisputedPayoutDistributionHash() == _payoutDistributionHash) {
                _payoutStake -= int256(Reporting.firstReportersDisputeBondAmount());
            }
        }
        if (address(_lastDisputeBond) != address(0)) {
            if (_lastDisputeBond.getDisputedPayoutDistributionHash() == _payoutDistributionHash) {
                _payoutStake -= int256(Reporting.lastReportersDisputeBondAmount());
            }
        }

        return _payoutStake;
    }

    function getMarketReportingState(IMarket _market) public view returns (IMarket.ReportingState) {
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
        bool _firstReportDisputed = address(_market.getFirstReportersDisputeBondToken()) != address(0);

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

        // If a first dispute bond has been posted we are in some phase of last reporting depending on time
        if (_firstReportDisputed) {
            if (_reportingWindow.isDisputeActive()) {
                if (_market.getTentativeWinningPayoutDistributionHash() == bytes32(0)) {
                    return IMarket.ReportingState.AWAITING_NO_REPORT_MIGRATION;
                } else {
                    return IMarket.ReportingState.LAST_DISPUTE;
                }
            }
            return IMarket.ReportingState.LAST_REPORTING;
        }

        // Either no designated report was made or the designated report was disputed so we are in some phase of first reporting
        if (_reportingWindow.isDisputeActive()) {
            if (_market.getTentativeWinningPayoutDistributionHash() == bytes32(0)) {
                return IMarket.ReportingState.AWAITING_NO_REPORT_MIGRATION;
            } else {
                return IMarket.ReportingState.FIRST_DISPUTE;
            }
        }

        return IMarket.ReportingState.FIRST_REPORTING;
    }
}
