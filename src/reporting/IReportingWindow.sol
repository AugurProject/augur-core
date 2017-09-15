pragma solidity ^0.4.13;

import 'ROOT/libraries/Typed.sol';
import 'ROOT/reporting/IBranch.sol';
import 'ROOT/reporting/IMarket.sol';
import 'ROOT/reporting/IRegistrationToken.sol';
import 'ROOT/reporting/IReputationToken.sol';
import 'ROOT/trading/ICash.sol';


contract IReportingWindow is Typed {
    function initialize(IBranch _branch, uint256 _reportingWindowId) public returns (bool);
    function createNewMarket(uint256 _endTime, uint8 _numOutcomes, uint256 _marketDenominator, uint256 _feePerEthInWei, ICash _denominationToken, address _creator, address _automatedReporterAddress, bytes32 _topic) public payable returns (IMarket _newMarket);
    function migrateMarketInFromSibling() public returns (bool);
    function migrateMarketInFromNibling() public returns (bool);
    function removeMarket() public returns (bool);
    function noteReport(IMarket _market, address _reporter, bytes32 _payoutDistributionHash) public returns (bool);
    function updateMarketPhase() public returns (bool);
    function getBranch() public constant returns (IBranch);
    function getReputationToken() public constant returns (IReputationToken);
    function getRegistrationToken() public constant returns (IRegistrationToken);
    function getStartTime() public constant returns (uint256);
    function getEndTime() public constant returns (uint256);
    function checkIn() public returns (bool);
    function isContainerForRegistrationToken(IRegistrationToken _shadyRegistrationToken) public constant returns (bool);
    function isContainerForMarket(IMarket _shadyMarket) public constant returns (bool);
    function isDoneReporting(address _reporter) public constant returns (bool);
    function isForkingMarketFinalized() public constant returns (bool);
    function isDisputeActive() public constant returns (bool);
}
