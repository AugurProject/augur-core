pragma solidity 0.4.18;


import 'libraries/ITyped.sol';
import 'libraries/IOwnable.sol';
import 'trading/ICash.sol';
import 'trading/IShareToken.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReportingWindow.sol';
import 'reporting/IStakeToken.sol';
import 'reporting/IDisputeBond.sol';
import 'trading/IShareToken.sol';
import 'libraries/IMailbox.sol';


contract IMarket is ITyped, IOwnable {
    enum ReportingState {
        PRE_REPORTING,
        DESIGNATED_REPORTING,
        AWAITING_FORK_MIGRATION,
        DESIGNATED_DISPUTE,
        FIRST_REPORTING,
        FIRST_DISPUTE,
        AWAITING_NO_REPORT_MIGRATION,
        LAST_REPORTING,
        LAST_DISPUTE,
        FORKING,
        AWAITING_FINALIZATION,
        FINALIZED
    }

    function initialize(IReportingWindow _reportingWindow, uint256 _endTime, uint8 _numOutcomes, uint256 _numTicks, uint256 _feeDivisor, ICash _cash, address _creator, address _designatedReporterAddress) public payable returns (bool _success);
    function updateTentativeWinningPayoutDistributionHash(bytes32 _payoutDistributionHash) public returns (bool);
    function derivePayoutDistributionHash(uint256[] _payoutNumerators, bool _invalid) public view returns (bytes32);
    function designatedReport() public returns (bool);
    function getUniverse() public view returns (IUniverse);
    function getReportingWindow() public view returns (IReportingWindow);
    function getNumberOfOutcomes() public view returns (uint8);
    function getNumTicks() public view returns (uint256);
    function getDenominationToken() public view returns (ICash);
    function getShareToken(uint8 _outcome)  public view returns (IShareToken);
    function getDesignatedReporter() public view returns (address);
    function getDesignatedReporterDisputeBond() public view returns (IDisputeBond);
    function getFirstReportersDisputeBond() public view returns (IDisputeBond);
    function getLastReportersDisputeBond() public view returns (IDisputeBond);
    function getMarketCreatorSettlementFeeDivisor() public view returns (uint256);
    function getReportingState() public view returns (ReportingState);
    function getFinalizationTime() public view returns (uint256);
    function getFinalPayoutDistributionHash() public view returns (bytes32);
    function getDesignatedReportPayoutHash() public view returns (bytes32);
    function getFinalWinningStakeToken() public view returns (IStakeToken);
    function getStakeTokenOrZeroByPayoutDistributionHash(bytes32 _payoutDistributionHash) public view returns (IStakeToken);
    function getTentativeWinningPayoutDistributionHash() public view returns (bytes32);
    function getBestGuessSecondPlaceTentativeWinningPayoutDistributionHash() public view returns (bytes32);
    function getForkingMarket() public view returns (IMarket _market);
    function getEndTime() public view returns (uint256);
    function getDesignatedReportDueTimestamp() public view returns (uint256);
    function getDesignatedReportReceivedTime() public view returns (uint256);
    function getDesignatedReportDisputeDueTimestamp() public view returns (uint256);
    function getTotalStake() public view returns (uint256);
    function getTotalWinningDisputeBondStake() public view returns (uint256);
    function getExtraDisputeBondRemainingToBePaidOut() public view returns (uint256);
    function getMarketCreatorMailbox() public view returns (IMailbox);
    function decreaseExtraDisputeBondRemainingToBePaidOut(uint256 _amount) public returns (bool);
    function firstReporterCompensationCheck(address _reporter) public returns (uint256);
    function increaseTotalStake(uint256 _amount) public returns (bool);
    function migrateDueToNoReports() public returns (bool);
    function isContainerForStakeToken(IStakeToken _shadyTarget) public view returns (bool);
    function isContainerForDisputeBond(IDisputeBond _shadyTarget) public view returns (bool);
    function isContainerForShareToken(IShareToken _shadyTarget) public view returns (bool);
    function isValid() public view returns (bool);
}
