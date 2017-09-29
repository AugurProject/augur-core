pragma solidity ^0.4.13;

import 'libraries/Typed.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IMarket.sol';
import 'reporting/IRegistrationToken.sol';
import 'reporting/IReputationToken.sol';
import 'trading/ICash.sol';


contract IReportingWindow is Typed {
    function initialize(IUniverse _universe, uint256 _reportingWindowId) public returns (bool);
    function createNewMarket(uint256 _endTime, uint8 _numOutcomes, uint256 _numTicks, uint256 _feePerEthInWei, ICash _denominationToken, address _creator, address _designatedReporterAddress) public payable returns (IMarket _newMarket);
    function migrateMarketInFromSibling() public returns (bool);
    function migrateMarketInFromNibling() public returns (bool);
    function removeMarket() public returns (bool);
    function noteReport(IMarket _market, address _reporter, bytes32 _payoutDistributionHash) public returns (bool);
    function updateMarketPhase() public returns (bool);
    function getUniverse() public constant returns (IUniverse);
    function getReputationToken() public constant returns (IReputationToken);
    function getRegistrationToken() public constant returns (IRegistrationToken);
    function getStartTime() public constant returns (uint256);
    function getEndTime() public constant returns (uint256);
    function getNumMarkets() public constant returns (uint256);
    function getNumIndeterminateMarkets() public constant returns (uint256);
    function checkIn() public returns (bool);
    function isContainerForRegistrationToken(IRegistrationToken _shadyRegistrationToken) public constant returns (bool);
    function isContainerForMarket(IMarket _shadyMarket) public constant returns (bool);
    function isDoneReporting(address _reporter) public constant returns (bool);
    function isForkingMarketFinalized() public constant returns (bool);
    function isDisputeActive() public constant returns (bool);
}
