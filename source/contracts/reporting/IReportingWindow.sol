pragma solidity 0.4.17;


import 'libraries/ITyped.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IMarket.sol';
import 'reporting/IReputationToken.sol';
import 'trading/ICash.sol';


contract IReportingWindow is ITyped {
    function initialize(IUniverse _universe, uint256 _reportingWindowId) public returns (bool);
    function createMarket(uint256 _endTime, uint8 _numOutcomes, uint256 _numTicks, uint256 _feePerEthInWei, ICash _denominationToken, address _designatedReporterAddress) public payable returns (IMarket _newMarket);
    function migrateMarketInFromSibling() public returns (bool);
    function migrateMarketInFromNibling() public returns (bool);
    function removeMarket() public returns (bool);
    function noteReportingGasPrice(IMarket _market) public returns (bool);
    function updateMarketPhase() public returns (bool);
    function getUniverse() public view returns (IUniverse);
    function getReputationToken() public view returns (IReputationToken);
    function getStartTime() public view returns (uint256);
    function getEndTime() public view returns (uint256);
    function getNumMarkets() public view returns (uint256);
    function getNumInvalidMarkets() public view returns (uint256);
    function getNumIncorrectDesignatedReportMarkets() public view returns (uint256);
    function getAvgReportingGasPrice() public view returns (uint256);
    function getNextReportingWindow() public returns (IReportingWindow);
    function getPreviousReportingWindow() public returns (IReportingWindow);
    function getNumDesignatedReportNoShows() public view returns (uint256);
    function allMarketsFinalized() public view returns (bool);
    function collectReportingFees(address _reporterAddress, uint256 _attoStakeTokens, bool _forgoFees) public returns (bool);
    function triggerMigrateFeesDueToFork(IReportingWindow _reportingWindow) public returns (bool);
    function migrateFeesDueToFork() public returns (bool);
    function isContainerForMarket(ITyped _shadyTarget) public view returns (bool);
    function isForkingMarketFinalized() public view returns (bool);
    function isDisputeActive() public view returns (bool);
}
