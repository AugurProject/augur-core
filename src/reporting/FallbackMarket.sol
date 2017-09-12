pragma solidity ^0.4.13;

import 'ROOT/reporting/IBranch.sol';
import 'ROOT/reporting/IMarket.sol';
import 'ROOT/libraries/DelegationTarget.sol';
import 'ROOT/libraries/Initializable.sol';
import 'ROOT/libraries/Ownable.sol';
import 'ROOT/factories/ReportingTokenFactory.sol';
import 'ROOT/reporting/IReportingToken.sol';



contract FallbackMarket is DelegationTarget, Typed, Initializable, Ownable, IMarket {
    IReportingWindow private reportingWindow;
    IReportingToken private reportingToken;

    function initialize(IReportingWindow _reportingWindow, uint256 _endTime, uint8 _numOutcomes, uint256 _payoutDenominator, uint256 _feePerEthInAttoeth, ICash _cash, address _creator, int256 _minDisplayPrice, int256 _maxDisplayPrice, address _automatedReporterAddress, bytes32 _topic) public payable beforeInitialized returns (bool _success) {
        endInitialization();
        reportingWindow = _reportingWindow;
        uint256[] memory _payoutNumerators;
        reportingToken = ReportingTokenFactory(controller.lookup("ReportingTokenFactory")).createReportingToken(controller, this, _payoutNumerators);
        return true;
    }

    function updateTentativeWinningPayoutDistributionHash(bytes32 _payoutDistributionHash) public returns (bool) {
        return false;
    }

    function derivePayoutDistributionHash(uint256[] _payoutNumerators) public constant returns (bytes32) {
        return sha3(_payoutNumerators);
    }

    function getTypeName() public constant returns (bytes32) {
        return "FallbackMarket";
    }

    function getBranch() public constant returns (IBranch) {
        return reportingWindow.getBranch();
    }

    function getReportingWindow() public constant returns (IReportingWindow) {
        return reportingWindow;
    }

    function getNumberOfOutcomes() public constant returns (uint8) {
        return 0;
    }

    function getMinDisplayPrice() public constant returns (int256) {
        return 0;
    }

    function getMaxDisplayPrice() public constant returns (int256) {
        return 0;
    }

    function getCompleteSetCostInAttotokens() public constant returns (uint256) {
        return 0;
    }

    function getPayoutDenominator() public constant returns (uint256) {
        return 1;
    }

    function getTopic() public constant returns (bytes32) {
        return "";
    }

    function getDenominationToken() public constant returns (ICash) {
        return ICash(0);
    }

    function getShareToken(uint8 _outcome)  public constant returns (IShareToken) {
        return IShareToken(0);
    }

    function getAutomatedReporterDisputeBondToken() public constant returns (IDisputeBond) {
        return IDisputeBond(0);
    }

    function getLimitedReportersDisputeBondToken() public constant returns (IDisputeBond) {
        return IDisputeBond(0);
    }

    function getMarketCreatorSettlementFeeInAttoethPerEth() public constant returns (uint256) {
        return 0;
    }

    function getReportingState() public constant returns (ReportingState) {
        return ReportingState.LIMITED_REPORTING;
    }

    function getFinalizationTime() public constant returns (uint256) {
        return 0;
    }

    function getFinalPayoutDistributionHash() public constant returns (bytes32) {
        return bytes32(0);
    }

    function getFinalWinningReportingToken() public constant returns (IReportingToken) {
        return IReportingToken(0);
    }

    function getReportingTokenOrZeroByPayoutDistributionHash(bytes32 _payoutDistributionHash) public constant returns (IReportingToken) {
        return reportingToken;
    }

    function isContainerForReportingToken(Typed _shadyTarget) public constant returns (bool) {
        return address(_shadyTarget) == address(reportingToken);
    }

    function isContainerForDisputeBondToken(Typed _shadyTarget) public constant returns (bool) {
        return false;
    }

    function isContainerForShareToken(Typed _shadyTarget) public constant returns (bool) {
        return false;
    }

    // Helpers

    function getReportingToken(uint256[] _payoutNumerators) public returns (IReportingToken) {
        return reportingToken;
    }
}
