pragma solidity ^0.4.13;

import 'ROOT/reporting/ReportingWindow.sol';
import 'ROOT/reporting/Market.sol';


/**
 * @title MarketExtensions
 * @dev functions moved from the market contract into a library to reduce the size of the market contract under the EVM limit
 */
contract MarketExtensions {
    function getWinningPayoutDistributionHashFromFork(Market _market) public constant returns (bytes32) {
        ReportingWindow _reportingWindow = _market.getReportingWindow();
        if (_reportingWindow.getBranch().getForkingMarket() != _market) {
            return 0;
        }
        ReputationToken _winningDestination = _reportingWindow.getReputationToken().getTopMigrationDestination();
        if (address(_winningDestination) == address(0)) {
            return 0;
        }
        uint256 _halfTotalSupply = 11 * 10**6 * 10**18 / 2;
        if (_winningDestination.totalSupply() < _halfTotalSupply && block.timestamp < _reportingWindow.getBranch().getForkEndTime()) {
            return 0;
        }
        return _winningDestination.getBranch().getParentPayoutDistributionHash();
    }
}
