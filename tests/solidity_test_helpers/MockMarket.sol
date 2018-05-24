pragma solidity ^0.4.20;

import 'reporting/IMarket.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IMailbox.sol';
import 'libraries/ITyped.sol';


contract MockMarket is IMarket {
    IUniverse private universe;
    bool private designatedReportValue;
    bytes32 private derivePayoutDistributionHashValue;
    bytes32 private updateDerivePayoutDistributionHashValue;
    IFeeWindow private feeWindow;
    IFeeWindow private setMigrateDueToNoReportsNextStateValue;
    uint256 private numberOfOutcomes;
    uint256 private numTicks;
    ICash private denominationToken;
    IShareToken private shareToken;
    address private designatedReporter;
    uint256 private marketCreatorSettlementFeeDivisor;
    uint256 private finalizationTime;
    bytes32 private finalPayoutDistributionHash;
    bytes32 private designatedReportPayoutHash;
    bytes32 private tentativeWinningPayoutDistributionHash;
    bytes32 private bestGuessSecondPlaceTentativeWinningPayoutDistributionHash;
    IMarket private forkingMarket;
    uint256 private endTime;
    uint256 private designatedReportDueTimestamp;
    uint256 private designatedReportReceivedTime;
    uint256 private designatedReportDisputeDueTimestamp;
    uint256 private firstReporterCompCheck;
    bool private migrateDueToNoRep;
    bool private isContForShareToken;
    bool private isInValidValue;
    address private owner;
    bool private transferOwner;
    IUniverse private initializeUniverseValue;
    uint256 private initializeEndTime;
    uint256 private initializeNumOutcomesValue;
    uint256 private initializeNumTicksValue;
    uint256 private initializeFeePerEthInAttoethValue;
    ICash private initializeCashValue;
    address private initializeCreatorValue;
    address private initializeDesignatedReporterAddressValue;
    IMailbox private setMarketCreatorMailbox;
    bool private setDesignatedReporterWasCorrectValue;
    bool private setDesignatedReporterShowedValue;
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

    function setFeeWindow(IFeeWindow _feeWindow) public {
        feeWindow = _feeWindow;
    }

    function setNumberOfOutcomes(uint256 _numberOfOutcomes) public {
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

    function setMarketCreatorSettlementFeeDivisor(uint256 _marketCreatorSettlementFeeDivisor) public {
        marketCreatorSettlementFeeDivisor = _marketCreatorSettlementFeeDivisor;
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

    function setFirstReporterCompensationCheck(uint256 _firstReporterCompCheck) public {
        firstReporterCompCheck = _firstReporterCompCheck;
    }

    function setMigrateDueToNoReports(bool _migrateDueToNoRep) public {
        migrateDueToNoRep = _migrateDueToNoRep;
    }

    function setIsContainerForShareToken(bool _isContForShareToken) public {
        isContForShareToken = _isContForShareToken;
    }

    function setIsInvalid(bool _isInValidValue) public {
        isInValidValue = _isInValidValue;
    }

    function setOwner(address _owner) public {
        owner = _owner;
    }

    function setTransferOwnership(bool _transferOwner) public {
        transferOwner = _transferOwner;
    }

    function callForkOnUniverse(IUniverse _universe) public returns(bool) {
        return _universe.fork();
    }

    function getInitializeUniverseValue() public view returns (IUniverse) {
        return initializeUniverseValue;
    }

    function getInitializeEndTime() public returns(uint256) {
        return initializeEndTime;
    }

    function getInitializeNumOutcomesValue() public returns(uint256) {
        return initializeNumOutcomesValue;
    }

    function getInitializeNumTicksValue() public returns(uint256) {
        return initializeNumTicksValue;
    }

    function getInitializeFeePerEthInAttoethValue() public returns(uint256) {
        return initializeFeePerEthInAttoethValue;
    }

    function getInitializeCashValue() public view returns(ICash) {
        return initializeCashValue;
    }

    function getInitializeCreatorValue() public returns(address) {
        return initializeCreatorValue;
    }

    function getInitializeDesignatedReporterAddressValue() public returns(address) {
        return initializeDesignatedReporterAddressValue;
    }

    function getUpdateDerivePayoutDistributionHashValue() public returns(bytes32) {
        return updateDerivePayoutDistributionHashValue;
    }

    function setMigrateDueToNoReportsNextState(IFeeWindow _feeWindow) public {
        setMigrateDueToNoReportsNextStateValue = _feeWindow;
    }

    function callTrustedMarketTransfer(IReputationToken _reputationToken, address _source, address _destination, uint256 _attotokens) public returns (bool) {
        return _reputationToken.trustedMarketTransfer(_source, _destination, _attotokens);
    }

    function setMarketCreatorMailboxValue(IMailbox _setMarketCreatorMailbox) public {
        setMarketCreatorMailbox = _setMarketCreatorMailbox;
    }

    function callOnMarketFinalized(IFeeWindow _feeWindow) public returns(bool) {
        return _feeWindow.onMarketFinalized();
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

    function initialize(IUniverse _universe, uint256 _endTime, uint256 _feePerEthInAttoeth, ICash _cash, address _designatedReporterAddress, address _creator, uint256 _numOutcomes, uint256 _numTicks) public payable returns (bool _success) {
        initializeUniverseValue = _universe;
        initializeEndTime = _endTime;
        initializeNumOutcomesValue = _numOutcomes;
        initializeNumTicksValue = _numTicks;
        initializeFeePerEthInAttoethValue = _feePerEthInAttoeth;
        initializeCashValue = _cash;
        initializeCreatorValue = _creator;
        initializeDesignatedReporterAddressValue = _designatedReporterAddress;
        return true;
    }

    function updateTentativeWinningPayoutDistributionHash(bytes32 _payoutDistributionHash) public returns (bool) {
        updateDerivePayoutDistributionHashValue = _payoutDistributionHash;
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

    function getFeeWindow() public view returns (IFeeWindow) {
        return feeWindow;
    }

    function getNumberOfOutcomes() public view returns (uint256) {
        return numberOfOutcomes;
    }

    function getNumTicks() public view returns (uint256) {
        return numTicks;
    }

    function getDenominationToken() public view returns (ICash) {
        return denominationToken;
    }

    function getShareToken(uint256 _outcome)  public view returns (IShareToken) {
        return shareToken;
    }

    function getDesignatedReporter() public view returns (address) {
        return designatedReporter;
    }

    function getMarketCreatorSettlementFeeDivisor() public view returns (uint256) {
        return marketCreatorSettlementFeeDivisor;
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

    function firstReporterCompensationCheck(address _reporter) public returns (uint256) {
        return firstReporterCompCheck;
    }

    function migrateDueToNoReports() public returns (bool) {
        // :TODO, some reason this doesn't work. figure out how to move state
        // setFeeWindow(setMigrateDueToNoReportsNextStateValue);
        return migrateDueToNoRep;
    }

    function isContainerForShareToken(IShareToken _shadyTarget) public view returns (bool) {
        return isContForShareToken;
    }

    function isInvalid() public view returns (bool) {
        return isInValidValue;
    }

    function getMarketCreatorMailbox() public view returns (IMailbox) {
        return setMarketCreatorMailbox;
    }

    function disavowTokens() public returns (bool) {
        return true;
    }

    function getWinningPayoutDistributionHash() public view returns (bytes32) {
        return bytes32(0);
    }

    function getWinningPayoutNumerator(uint256 _outcome) public view returns (uint256) {
        return 0;
    }

    function getReputationToken() public view returns (IReputationToken) {
        return IReputationToken(0);
    }

    function isContainerForReportingParticipant(IReportingParticipant _reportingParticipant) public view returns (bool) {
        return true;
    }

    function finishedCrowdsourcingDisputeBond() public returns (bool) {
        return true;
    }

    function setDesignatedReporterWasCorrect(bool _designatedReporterWasCorrect) public { setDesignatedReporterWasCorrectValue = _designatedReporterWasCorrect; }

    function designatedReporterWasCorrect() public view returns (bool) {
        return setDesignatedReporterWasCorrectValue;
    }

    function setDesignatedReporterShowed(bool _designatedReporterShowed) public { setDesignatedReporterShowedValue = _designatedReporterShowed; }

    function designatedReporterShowed() public view returns (bool) {
        return setDesignatedReporterShowedValue;
    }

    function isFinalized() public view returns (bool) {
        return true;
    }

    function finalizeFork() public returns (bool) {
        return true;
    }

    function assertBalances() public view returns (bool) {
        return true;
    }

    function finalize() public returns (bool) {
        return true;
    }

    function onTransferOwnership(address, address) internal returns (bool) {
        return true;
    }

    function getInitialReporterAddress() public view returns (address) {
        return address(0);
    }

    function deriveMarketCreatorFeeAmount(uint256 _amount) public view returns (uint256) {
        return 0;
    }
}
