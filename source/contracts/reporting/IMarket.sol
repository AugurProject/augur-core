pragma solidity 0.4.17;


import 'libraries/ITyped.sol';
import 'libraries/IOwnable.sol';
import 'trading/ICash.sol';
import 'trading/IShareToken.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReportingWindow.sol';
import 'reporting/IStakeToken.sol';
import 'reporting/IDisputeBond.sol';
import 'trading/IShareToken.sol';


contract IMarket is ITyped, IOwnable {
    enum ReportingState {
        PRE_REPORTING,
        DESIGNATED_REPORTING,
        DESIGNATED_DISPUTE,
        AWAITING_FORK_MIGRATION,
        ROUND1_REPORTING,
        FIRST_DISPUTE,
        AWAITING_NO_REPORT_MIGRATION,
        ROUND2_REPORTING,
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
    function getDesignatedReporterDisputeBondToken() public view returns (IDisputeBond);
    function getRound1ReportersDisputeBondToken() public view returns (IDisputeBond);
    function getRound2ReportersDisputeBondToken() public view returns (IDisputeBond);
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
    function round1ReporterCompensationCheck(address _reporter) public returns (uint256);
    function increaseTotalStake(uint256 _amount) public returns (bool);
    function migrateDueToNoReports() public returns (bool);
    function isContainerForStakeToken(ITyped _shadyTarget) public view returns (bool);
    function isContainerForDisputeBondToken(ITyped _shadyTarget) public view returns (bool);
    function isContainerForShareToken(ITyped _shadyTarget) public view returns (bool);
    function isValid() public view returns (bool);
}
