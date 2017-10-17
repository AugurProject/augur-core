pragma solidity ^0.4.17;

import 'reporting/IMarket.sol';
import 'reporting/IUniverse.sol';
import 'libraries/ITyped.sol';

contract MockMarket is IMarket {
    IUniverse private universe;
    bool private designatedReportValue;
    bytes32 private derivePayoutDistributionHashValue;
    IReportingWindow private reportingWindow;
    uint8 private numberOfOutcomes;
    uint256 private numTicks;
    ICash private denominationToken;
    IShareToken private shareToken;
    address private designatedReporter;
    IDisputeBond private disputeBond;
    IDisputeBond private round1DisputeBond;
    IDisputeBond private round2DisputeBond;
    uint256 private marketCreatorSettlementFeeInAttoethPerEth;
    ReportingState private reportingState;
    uint256 private finalizationTime;
    bytes32 private finalPayoutDistributionHash;
    bytes32 private designatedReportPayoutHash;
    IStakeToken private finalWinningStakeToken;
    IStakeToken private stakeTokenOrZeroByPayoutDistributionHash;
    bytes32 private tentativeWinningPayoutDistributionHash;
    bytes32 private bestGuessSecondPlaceTentativeWinningPayoutDistributionHash;
    IMarket private forkingMarket;
    uint256 private endTime;
    uint256 private designatedReportDueTimestamp;
    uint256 private designatedReportReceivedTime;
    uint256 private designatedReportDisputeDueTimestamp;
    uint256 private round1ReporterCompCheck;
    bool private migrateDueToNoRep;
    bool private isContForStakeToken;
    bool private isContForDisputeBondToken;
    bool private isContForShareToken;
    bool private isValidValue;
    address private owner;
    bool private transferOwner;

    /*
    * setters to feed the getters and impl of IMarket
    */
    function setUniverse(IUniverse _universe) public { 
        universe = _universe; 
    }
    
    function setDesignatedReport(bool _designatedReportValue) public {
        designatedReportValue = _designatedReportValue;
    }
    
    function setDerivePayoutDistributionHash(bytes32 _derivePayoutDistributionHashValue) public {
        derivePayoutDistributionHashValue = _derivePayoutDistributionHashValue;
    }
    
    function setReportingWindow(IReportingWindow _reportingWindow) public {
        reportingWindow = _reportingWindow;
    }

    function setNumberOfOutcomes(uint8 _numberOfOutcomes) public {
        numberOfOutcomes = _numberOfOutcomes;
    }

    function setNumTicks(uint256 _numTicks) public {
        numTicks = _numTicks;
    }

    function setDenominationToken(ICash _denominationToken) public {
        denominationToken = _denominationToken;
    }

    function setShareToken(IShareToken _shareToken)  public {
        shareToken = _shareToken;
    }

    function setDesignatedReporter(address _designatedReporter) public {
        designatedReporter = _designatedReporter;
    }

    function setDesignatedReporterDisputeBondToken(IDisputeBond _disputeBond) public {
        disputeBond = _disputeBond;
    }

    function setRound1ReportersDisputeBondToken(IDisputeBond _round1DisputeBond) public {
        round1DisputeBond = _round1DisputeBond;
    }

    function setRound2ReportersDisputeBondToken(IDisputeBond _round2DisputeBond) public {
        round2DisputeBond = _round2DisputeBond;
    }

    function setMarketCreatorSettlementFeeInAttoethPerEth(uint256 _marketCreatorSettlementFeeInAttoethPerEth) public {
        marketCreatorSettlementFeeInAttoethPerEth = _marketCreatorSettlementFeeInAttoethPerEth;
    }

    function setReportingState(ReportingState _reportingState) public {
        reportingState = _reportingState;
    }

    function setFinalizationTime(uint256 _finalizationTime) public {
        finalizationTime = _finalizationTime;
    }

    function setFinalPayoutDistributionHash(bytes32 _finalPayoutDistributionHash) public {
        finalPayoutDistributionHash = _finalPayoutDistributionHash;
    }
    
    function setDesignatedReportPayoutHash(bytes32 _designatedReportPayoutHash) public {
        designatedReportPayoutHash = _designatedReportPayoutHash;
    }

    function setFinalWinningStakeToken(IStakeToken _finalWinningStakeToken) public {
        finalWinningStakeToken = _finalWinningStakeToken;
    }

    function setStakeTokenOrZeroByPayoutDistributionHash(IStakeToken _stakeTokenOrZeroByPayoutDistributionHash) public {
        stakeTokenOrZeroByPayoutDistributionHash = _stakeTokenOrZeroByPayoutDistributionHash;
    }

    function setTentativeWinningPayoutDistributionHash(bytes32 _tentativeWinningPayoutDistributionHash) public {
        tentativeWinningPayoutDistributionHash = _tentativeWinningPayoutDistributionHash;
    }

    function setBestGuessSecondPlaceTentativeWinningPayoutDistributionHash(bytes32 _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash) public {
        bestGuessSecondPlaceTentativeWinningPayoutDistributionHash = _bestGuessSecondPlaceTentativeWinningPayoutDistributionHash;
    }

    function setForkingMarket(IMarket _forkingMarket) public {
        forkingMarket = _forkingMarket;
    }

    function setEndTime(uint256 _endTime) public {
        endTime = _endTime;
    }

    function setDesignatedReportDueTimestamp(uint256 _designatedReportDueTimestamp) public {
        designatedReportDueTimestamp = _designatedReportDueTimestamp;
    }

    function setDesignatedReportReceivedTime(uint256 _designatedReportReceivedTime) public {
        designatedReportReceivedTime = _designatedReportReceivedTime;
    }

    function setDesignatedReportDisputeDueTimestamp(uint256 _designatedReportDisputeDueTimestamp) public {
        designatedReportDisputeDueTimestamp = _designatedReportDisputeDueTimestamp;
    }

    function setRound1ReporterCompensationCheck(uint256 _round1ReporterCompCheck) public {
        round1ReporterCompCheck = _round1ReporterCompCheck;
    }

    function setMigrateDueToNoReports(bool _migrateDueToNoRep) public {
        migrateDueToNoRep = _migrateDueToNoRep;
    }

    function setIsContainerForStakeToken(bool _isContForStakeToken) {
        isContForStakeToken = _isContForStakeToken;
    }

    function setIsContainerForDisputeBondToken(bool _isContForDisputeBondToken) public {
        isContForDisputeBondToken = _isContForDisputeBondToken;
    }

    function setIsContainerForShareToken(bool _isContForShareToken) public {
        isContForShareToken = _isContForShareToken;
    }

    function setIsValid(bool _isValidValue) public {
        isValidValue = _isValidValue;
    }

    function setOwner(address _owner) public {
        owner = _owner;
    }

    function setTransferOwnership(bool _transferOwner) public {
        transferOwner = _transferOwner;
    }

    function callStakeTokenTrustedBuy(IStakeToken _stakeToken, address _reporter, uint256 _attotokens) public returns (bool) {
        return _stakeToken.trustedBuy(_reporter, _attotokens); 
    }
    
    /*
    * IMarket methods
    */

    function getOwner() public view returns (address) { 
        return owner;
    }

    function transferOwnership(address newOwner) public returns (bool) {
        return transferOwner;
    }

    function getTypeName() public view returns (bytes32) {
        return "Market";
    }

    function initialize(IReportingWindow _reportingWindow, uint256 _endTime, uint8 _numOutcomes, uint256 _numTicks, uint256 _feePerEthInAttoeth, ICash _cash, address _creator, address _designatedReporterAddress) public payable returns (bool _success) {
        return true;
    }

    function updateTentativeWinningPayoutDistributionHash(bytes32 _payoutDistributionHash) public returns (bool) { 
        derivePayoutDistributionHashValue = _payoutDistributionHash; 
        return true; 
    }

    function derivePayoutDistributionHash(uint256[] _payoutNumerators, bool _invalid) public view returns (bytes32) {
        return derivePayoutDistributionHashValue;
    }

    function designatedReport() public returns (bool) {
        return designatedReportValue;
    }

    function getUniverse() public view returns (IUniverse) {
        return universe;
    }

    function getReportingWindow() public view returns (IReportingWindow) {
        return reportingWindow;
    }

    function getNumberOfOutcomes() public view returns (uint8) {
        return numberOfOutcomes;
    }
    
    function getNumTicks() public view returns (uint256) {
        return numTicks;
    }

    function getDenominationToken() public view returns (ICash) {
        return denominationToken;
    }
    
    function getShareToken(uint8 _outcome)  public view returns (IShareToken) {
        return shareToken;
    }

    function getDesignatedReporter() public view returns (address) {
        return designatedReporter;
    }

    function getDesignatedReporterDisputeBondToken() public view returns (IDisputeBond) {
        return disputeBond;
    }

    function getRound1ReportersDisputeBondToken() public view returns (IDisputeBond) {
        return round1DisputeBond;
    }
    
    function getRound2ReportersDisputeBondToken() public view returns (IDisputeBond) {
        return round2DisputeBond;
    }
    
    function getMarketCreatorSettlementFeeInAttoethPerEth() public view returns (uint256) {
        return marketCreatorSettlementFeeInAttoethPerEth;
    }

    function getReportingState() public view returns (ReportingState) {
        return reportingState;
    }

    function getFinalizationTime() public view returns (uint256) {
        return finalizationTime;
    }
    
    function getFinalPayoutDistributionHash() public view returns (bytes32) {
        return finalPayoutDistributionHash;
    }
    
    function getDesignatedReportPayoutHash() public view returns (bytes32) {
        return designatedReportPayoutHash;
    }
    
    function getFinalWinningStakeToken() public view returns (IStakeToken) {
        return finalWinningStakeToken;
    }
    
    function getStakeTokenOrZeroByPayoutDistributionHash(bytes32 _payoutDistributionHash) public view returns (IStakeToken) {
        return stakeTokenOrZeroByPayoutDistributionHash;
    }
    
    function getTentativeWinningPayoutDistributionHash() public view returns (bytes32) {
        return tentativeWinningPayoutDistributionHash;
    }
    
    function getBestGuessSecondPlaceTentativeWinningPayoutDistributionHash() public view returns (bytes32) {
        return bestGuessSecondPlaceTentativeWinningPayoutDistributionHash;
    }
    
    function getForkingMarket() public view returns (IMarket _market) {
        return forkingMarket;
    }
    
    function getEndTime() public view returns (uint256) {
        return endTime;
    }
    
    function getDesignatedReportDueTimestamp() public view returns (uint256) {
        return designatedReportDueTimestamp;
    }
    
    function getDesignatedReportReceivedTime() public view returns (uint256) {
        return designatedReportReceivedTime;
    }
    
    function getDesignatedReportDisputeDueTimestamp() public view returns (uint256) {
        return designatedReportDisputeDueTimestamp;
    }
    
    function round1ReporterCompensationCheck(address _reporter) public returns (uint256) {
        return round1ReporterCompCheck;
    }
    
    function migrateDueToNoReports() public returns (bool) {
        return migrateDueToNoRep;
    }
    
    function isContainerForStakeToken(ITyped _shadyTarget) public view returns (bool) {
        return isContForStakeToken;
    }
    
    function isContainerForDisputeBondToken(ITyped _shadyTarget) public view returns (bool) {
        return isContForDisputeBondToken;
    }
    
    function isContainerForShareToken(ITyped _shadyTarget) public view returns (bool) {
        return isContForShareToken;
    }
    
    function isValid() public view returns (bool) {
        return isValidValue;
    }
}
