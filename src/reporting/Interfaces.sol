pragma solidity ^0.4.13;

import 'ROOT/libraries/token/ERC20.sol';
import 'ROOT/libraries/token/VariableSupplyToken.sol';


contract IBranch {
    function getParentBranch() constant returns (IBranch);
    function getChildBranch(int256 _payoutDistributionHash) constant returns (IBranch);
    function getReputationToken() constant returns (IReputationToken);
    function getForkingMarket() constant returns (IMarket);
    function isParentOf(IBranch _branch) constant returns (bool);
    function isContainerForReportingWindow(address _shadyReportingWindow) constant returns (bool);
    function isContainerForRegistrationToken(address _shadyRegistrationToken) constant returns (bool);
    function isContainerForMarket(address _shadyMarket) constant returns (bool);
    function isContainerForReportingToken(address _shadyReportingToken) constant returns (bool);
    function getReportingWindowByTimestamp(int256 _timestamp) constant public returns (IReportingWindow);
    function getReportingWindowByMarketEndTime(int256 _endTime, int256 _hasAutomatedReporter) returns (IReportingWindow);
}


contract IReputationToken is ERC20 {
    function getBranch() constant returns (IBranch);
    function migrateOut(IReputationToken _destination, address _reporter, uint256 _attotokens) public returns (bool);
    function migrateIn(address _reporter, uint256 _attotokens) public returns (bool);
    function trustedTransfer(address _source, address _destination, uint256 _amount) public returns (bool);
}


contract IReportingWindow {
    function noteReport(IMarket, address, int256) public returns (bool);
    function getStartTime() public returns (int256);
    function getBranch() public returns (IBranch);
    function createNewMarket(int256 _endTime, int256 _numOutcomes, int256 _payoutDenominator, int256 _feePerEthInWei, address _denominationToken, address _sender, int256 _minDisplayPrice, int256 _maxDisplayPrice, address _automatedReporterAddress, int256 _topic) payable returns (IMarket);
}


contract IRegistrationToken is VariableSupplyToken {
    function register() public returns (bool);
    function redeem() public returns (bool);
}


contract IMarket {
    function getBranch() constant returns (IBranch);
    function getReputationToken() constant returns (IReputationToken);
    function getReportingWindow() constant returns (IReportingWindow);
    function getRegistrationToken() constant returns (IRegistrationToken);
    function getNumberOfOutcomes() constant returns (uint8);
    function getAutomatedReporterDisputeBondToken() constant returns (IDisputeBondToken);
    function getLimitedReportersDisputeBondToken() constant returns (IDisputeBondToken);
    function getAllReportersDisputeBondToken() constant returns (IDisputeBondToken);
    function isContainerForReportingToken(IReportingToken) constant returns (bool);
    function isFinalized() constant returns (bool);
    function canBeReportedOn() constant returns (bool);
    function getFinalWinningReportingToken() constant returns (IReportingToken);
    function getFinalPayoutDistributionHash() constant returns (int256);
    function derivePayoutDistributionHash(int256[]) constant returns (int256);
    function updateTentativeWinningPayoutDistributionHash(int256) public returns (bool);
}


contract IReportingToken {
    function buy(uint256 _amount) public returns (bool);
}


contract IDisputeBondToken {
    function getDisputedPayoutDistributionHash() constant returns (int256);
    function getBondRemainingToBePaidOut() constant returns (uint256);
}
