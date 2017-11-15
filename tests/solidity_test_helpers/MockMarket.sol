pragma solidity ^0.4.17;

import 'reporting/IMarket.sol';
import 'reporting/IUniverse.sol';
import 'libraries/ITyped.sol';
import 'libraries/IMailbox.sol';


contract MockMarket is IMarket {
    IUniverse private universe;
    bool private designatedReportValue;
    bytes32 private derivePayoutDistributionHashValue;
    bytes32 private updateDerivePayoutDistributionHashValue;
    IReportingWindow private reportingWindow;
    IReportingWindow private setMigrateDueToNoReportsNextStateValue;
    uint8 private numberOfOutcomes;
    uint256 private numTicks;
    ICash private denominationToken;
    IShareToken private shareToken;
    address private designatedReporter;
    IDisputeBond private disputeBond;
    IDisputeBond private firstDisputeBond;
    IDisputeBond private lastDisputeBond;
    uint256 private marketCreatorSettlementFeeDivisor;
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
    uint256 private firstReporterCompCheck;
    bool private migrateDueToNoRep;
    bool private isContForStakeToken;
    bool private isContForDisputeBond;
    bool private isContForShareToken;
    bool private isValidValue;
    address private owner;
    bool private transferOwner;
    IReportingWindow private initializeReportingWindowValue;
    uint256 private initializeEndTime;
    uint8 private initializeNumOutcomesValue;
    uint256 private initializeNumTicksValue;
    uint256 private initializeFeePerEthInAttoethValue;
    ICash private initializeCashValue;
    address private initializeCreatorValue;
    address private initializeDesignatedReporterAddressValue;
    bool private increaseTotalStakeValue;
    uint256 private setTotalWinningDisputeBondStakeValue;
    uint256 private setTotalStakeValue;
    uint256 private setExtraDisputeBondRemainingToBePaidOutValue;
    bool private setDecreaseExtraDisputeBondRemainingToBePaidOutValue;
    IMailbox private setMarketCreatorMailbox;
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

    function setDesignatedReporterDisputeBond(IDisputeBond _disputeBond) public {
        disputeBond = _disputeBond;
    }

    function setFirstReportersDisputeBond(IDisputeBond _firstDisputeBond) public {
        firstDisputeBond = _firstDisputeBond;
    }

    function setLastReportersDisputeBond(IDisputeBond _lastDisputeBond) public {
        lastDisputeBond = _lastDisputeBond;
    }

    function setMarketCreatorSettlementFeeDivisor(uint256 _marketCreatorSettlementFeeDivisor) public {
        marketCreatorSettlementFeeDivisor = _marketCreatorSettlementFeeDivisor;
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

    function setFirstReporterCompensationCheck(uint256 _firstReporterCompCheck) public {
        firstReporterCompCheck = _firstReporterCompCheck;
    }

    function setMigrateDueToNoReports(bool _migrateDueToNoRep) public {
        migrateDueToNoRep = _migrateDueToNoRep;
    }

    function setIsContainerForStakeToken(bool _isContForStakeToken) public {
        isContForStakeToken = _isContForStakeToken;
    }

    function setIsContainerForDisputeBond(bool _isContForDisputeBond) public {
        isContForDisputeBond = _isContForDisputeBond;
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

    function setIncreaseTotalStakeValue(bool _value) public {
        increaseTotalStakeValue = _value;
    }

    function setTotalWinningDisputeBondStake(uint256 _value) public {
        setTotalWinningDisputeBondStakeValue = _value;
    }

    function setTotalStake(uint256 _value) public {
        setTotalStakeValue = _value;
    }

    function setTransferOwnership(bool _transferOwner) public {
        transferOwner = _transferOwner;
    }

    function callStakeTokenTrustedBuy(IStakeToken _stakeToken, address _reporter, uint256 _attotokens) public returns (bool) {
        return _stakeToken.trustedBuy(_reporter, _attotokens);
    }

    function callReportingWindowMigrateMarketInFromSibling(IReportingWindow _reportingWindow) public returns(bool) {
        return _reportingWindow.migrateMarketInFromSibling();
    }

    function callReportingWindowMigrateMarketInFromNibling(IReportingWindow _reportingWindow) public returns(bool) {
        return _reportingWindow.migrateMarketInFromNibling();
    }

    function callReportingWindowRemoveMarket(IReportingWindow _reportingWindow) public returns(bool) {
        return _reportingWindow.removeMarket();
    }

    function callReportingWindowUpdateMarketPhase(IReportingWindow _reportingWindow) public returns(bool) {
        return _reportingWindow.updateMarketPhase();
    }

    function callIncreaseTotalStake(IReportingWindow _reportingWindow, uint256 _amount) public returns(bool) {
        return _reportingWindow.increaseTotalStake(_amount);
    }

    function callForkOnUniverse(IUniverse _universe) public returns(bool) {
        return _universe.fork();
    }

    function getInitializeReportingWindowValue() public view returns (IReportingWindow) {
        return initializeReportingWindowValue;
    }

    function getInitializeEndTime() public returns(uint256) {
        return initializeEndTime;
    }

    function getInitializeNumOutcomesValue() public returns(uint8) {
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

    function setMigrateDueToNoReportsNextState(IReportingWindow _reportingWindow) public {
        setMigrateDueToNoReportsNextStateValue = _reportingWindow;
    }

    function callTrustedMarketTransfer(IReputationToken _reputationToken, address _source, address _destination, uint256 _attotokens) public returns (bool) {
        return _reputationToken.trustedMarketTransfer(_source, _destination, _attotokens);
    }

    function setExtraDisputeBondRemainingToBePaidOut(uint256 _setExtraDisputeBondRemainingToBePaidOutValue) public {
        setExtraDisputeBondRemainingToBePaidOutValue = _setExtraDisputeBondRemainingToBePaidOutValue;
    }

    function setDecreaseExtraDisputeBondRemainingToBePaidOut(bool _setDecreaseExtraDisputeBondRemainingToBePaidOutValue) public {
        setDecreaseExtraDisputeBondRemainingToBePaidOutValue = _setDecreaseExtraDisputeBondRemainingToBePaidOutValue;
    }

    function setMarketCreatorMailboxValue(IMailbox _setMarketCreatorMailbox) public {
        setMarketCreatorMailbox = _setMarketCreatorMailbox;
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
        initializeReportingWindowValue = _reportingWindow;
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

    function getDesignatedReporterDisputeBond() public view returns (IDisputeBond) {
        return disputeBond;
    }

    function getFirstReportersDisputeBond() public view returns (IDisputeBond) {
        return firstDisputeBond;
    }

    function getLastReportersDisputeBond() public view returns (IDisputeBond) {
        return lastDisputeBond;
    }

    function getMarketCreatorSettlementFeeDivisor() public view returns (uint256) {
        return marketCreatorSettlementFeeDivisor;
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

    function firstReporterCompensationCheck(address _reporter) public returns (uint256) {
        return firstReporterCompCheck;
    }

    function migrateDueToNoReports() public returns (bool) {
        // :TODO, some reason this doesn't work. figure out how to move state
        // setReportingWindow(setMigrateDueToNoReportsNextStateValue);
        return migrateDueToNoRep;
    }

    function isContainerForStakeToken(IStakeToken _shadyTarget) public view returns (bool) {
        return isContForStakeToken;
    }

    function isContainerForDisputeBond(IDisputeBond _shadyTarget) public view returns (bool) {
        return isContForDisputeBond;
    }

    function isContainerForShareToken(IShareToken _shadyTarget) public view returns (bool) {
        return isContForShareToken;
    }

    function isValid() public view returns (bool) {
        return isValidValue;
    }

    function increaseTotalStake(uint256 _amount) public returns (bool) {
        return increaseTotalStakeValue;
    }

    function getTotalWinningDisputeBondStake() public view returns (uint256) {
        return setTotalWinningDisputeBondStakeValue;
    }

    function getTotalStake() public view returns (uint256) {
        return setTotalStakeValue;
    }

    function getExtraDisputeBondRemainingToBePaidOut() public view returns (uint256) {
        return setExtraDisputeBondRemainingToBePaidOutValue;
    }

    function decreaseExtraDisputeBondRemainingToBePaidOut(uint256 _amount) public returns (bool) {
        return setDecreaseExtraDisputeBondRemainingToBePaidOutValue;
    }

    function getMarketCreatorMailbox() public view returns (IMailbox) {
        return setMarketCreatorMailbox;
    }
}
