pragma solidity ^0.4.17;

import 'reporting/IMarket.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReportingWindow.sol';
import 'libraries/ITyped.sol';
import 'reporting/IReputationToken.sol';
import 'libraries/Initializable.sol';


contract MockReportingWindow is Initializable, IReportingWindow {
    bool private setMigrateMarketInFromSiblingValue;
    bool private setMigrateMarketInFromNiblingValue;
    bool private setRemoveMarketValue;
    bool private setNoteReportingGasPriceValue;
    bool private setUpdateMarketPhaseValue;
    IUniverse private universe;
    IReputationToken private setReputationTokenValue;
    uint256 private setStartTimeValue;
    uint256 private setEndTimeValue;
    uint256 private setNumMarketsValue;
    uint256 private setNumInvalidMarketsValue;
    uint256 private setNumIncorrectDesignatedReportMarketsValue;
    uint256 private setAvgReportingGasPriceValue;
    IReportingWindow private setNextReportingWindowValue;
    IReportingWindow private setPreviousReportingWindowValue;
    uint256 private setNumDesignatedReportNoShowsValue;
    bool private setAllMarketsFinalizedValue;
    bool private setCollectReportingFeesValue;
    bool private setTriggerMigrateFeesDueToForkValue;
    bool private setMigrateFeesDueToForkValue;
    bool private setIsContainerForMarketValue;
    bool private setIsForkingMarketFinalizedValue;
    bool private setIsDisputeActiveValue;
    IMarket private market;
    IUniverse private initializeUniverseValue;
    uint256 private initializeReportingWindowIdValue;
    address private collectReporterAddress;
    uint256 private collectAttoStakeTokens;
    bool private collectForgoFees;
    bool private setIsReportingActiveValue;
    bool private setIsActiveValue;
    bool private setIsOverValue;
    bool private setIsContainerForWindowParticipationTokenValue;
    bool private setIncreaseTotalStakeValue;
    bool private setIncreaseTotalWinningStakeValue;
    bool private setMigrateFeesDueToMarketMigrationValue;
    /*
    * setters to feed the getters and impl of IReportingWindow
    */
    function setMigrateMarketInFromSibling(bool _setMigrateMarketInFromSiblingValue) public {
        setMigrateMarketInFromSiblingValue = _setMigrateMarketInFromSiblingValue;
    }

    function setMigrateMarketInFromNibling(bool _setMigrateMarketInFromNiblingValue) public {
        setMigrateMarketInFromNiblingValue = _setMigrateMarketInFromNiblingValue;
    }

    function setRemoveMarket(bool _setRemoveMarketValue) public {
        setRemoveMarketValue = _setRemoveMarketValue;
    }
    
    function setNoteReportingGasPrice(bool _setNoteReportingGasPriceValue) public {
        setNoteReportingGasPriceValue = _setNoteReportingGasPriceValue;
    }
    
    function setUpdateMarketPhase(bool _setUpdateMarketPhaseValue) public {
        setUpdateMarketPhaseValue = _setUpdateMarketPhaseValue;
    }
    
    function setUniverse(IUniverse _universe) public {
        universe = _universe;
    }
    
    function setReputationToken(IReputationToken _setReputationTokenValue) public {
        setReputationTokenValue = _setReputationTokenValue;
    }
    
    function setStartTime(uint256 _setStartTimeValue) public {
        setStartTimeValue = _setStartTimeValue;
    }
    
    function setEndTime(uint256 _setEndTimeValue) public {
        setEndTimeValue = _setEndTimeValue;
    }

    function setNumMarkets(uint256 _setNumMarketsValue) public {
        setNumMarketsValue = _setNumMarketsValue;
    }

    function setNumInvalidMarkets(uint256 _setNumInvalidMarketsValue) public {
        setNumInvalidMarketsValue = _setNumInvalidMarketsValue;
    }

    function setNumIncorrectDesignatedReportMarkets(uint256 _setNumIncorrectDesignatedReportMarketsValue) public {
        setNumIncorrectDesignatedReportMarketsValue = _setNumIncorrectDesignatedReportMarketsValue;
    }

    function setAvgReportingGasPrice(uint256 _setAvgReportingGasPriceValue) public {
        setAvgReportingGasPriceValue = _setAvgReportingGasPriceValue;
    }

    function setNextReportingWindow(IReportingWindow _setNextReportingWindowValue) public {
        setNextReportingWindowValue = _setNextReportingWindowValue;
    }

    function setPreviousReportingWindow(IReportingWindow _setPreviousReportingWindowValue) public {
        setPreviousReportingWindowValue = _setPreviousReportingWindowValue;
    }

    function setNumDesignatedReportNoShows(uint256 _setNumDesignatedReportNoShowsValue) public {
        setNumDesignatedReportNoShowsValue = _setNumDesignatedReportNoShowsValue;
    }

    function setAllMarketsFinalized(bool _setAllMarketsFinalizedValue) public {
        setAllMarketsFinalizedValue = _setAllMarketsFinalizedValue;
    }

    function setCollectReportingFees(bool _setCollectReportingFeesValue) public {
        setCollectReportingFeesValue = _setCollectReportingFeesValue;
    }

    function setTriggerMigrateFeesDueToFork(bool _setTriggerMigrateFeesDueToForkValue) public {
        setTriggerMigrateFeesDueToForkValue = _setTriggerMigrateFeesDueToForkValue;
    }

    function setMigrateFeesDueToFork(bool _setMigrateFeesDueToForkValue) public {
        setMigrateFeesDueToForkValue = _setMigrateFeesDueToForkValue;
    }

    function setIsContainerForMarket(bool _setIsContainerForMarketValue) public {
        setIsContainerForMarketValue = _setIsContainerForMarketValue;
    }

    function setIsForkingMarketFinalized(bool _setIsForkingMarketFinalizedValue) public {
        setIsForkingMarketFinalizedValue = _setIsForkingMarketFinalizedValue;
    }

    function setIsDisputeActive(bool _setIsDisputeActiveValue) public {
        setIsDisputeActiveValue = _setIsDisputeActiveValue;
    }

    function setCreateMarket(IMarket _market) public {
        market = _market;
    }

    function setIsOver(bool _isOver) public {
        setIsOverValue = _isOver;
    }

    function setIsReportingActive(bool _isReportingActive) public {
        setIsReportingActiveValue = _isReportingActive;
    }

    function setIsActive(bool _isActive) public {
        setIsActiveValue = _isActive;
    }

    function setIsContainerForWindowParticipationToken(bool _isContainerForWindowParticipationToken) public {
        setIsContainerForWindowParticipationTokenValue = _isContainerForWindowParticipationToken;
    }

    function setIncreaseTotalStake(bool _setIncreaseTotalStakeValue) public {
        setIncreaseTotalStakeValue = _setIncreaseTotalStakeValue;
    }

    function setIncreaseTotalWinningStake(bool _setIncreaseTotalWinningStakeValue) public {
        setIncreaseTotalWinningStakeValue = _setIncreaseTotalWinningStakeValue;
    }

    function setMigrateFeesDueToMarketMigration(bool _setMigrateFeesDueToMarketMigration) public {
        setMigrateFeesDueToMarketMigrationValue = _setMigrateFeesDueToMarketMigration;
    }
    
    function getInitializeUniverseValue() public view returns(IUniverse) {
        return initializeUniverseValue;
    }

    function getinitializeReportingWindowIdValue() public returns(uint256) {
        return initializeReportingWindowIdValue;
    }

    function getCollectReporterAddress() public returns(address) {
        return collectReporterAddress;
    }

    function getCollectAttoStakeTokens() public returns(uint256) {
        return collectAttoStakeTokens;
    }

    function getCollectForgoFees() public returns(bool) {
        return collectForgoFees;
    }
    
    /*
    * Impl of IReportingWindow and ITyped
     */
    function getTypeName() public afterInitialized view returns (bytes32) {
        return "ReportingWindow";
    }

    function initialize(IUniverse _universe, uint256 _reportingWindowId) public returns (bool) {
        endInitialization();
        initializeUniverseValue = _universe;
        initializeReportingWindowIdValue = _reportingWindowId;
        return true;
    }

    function createMarket(uint256 _endTime, uint8 _numOutcomes, uint256 _numTicks, uint256 _feePerEthInWei, ICash _denominationToken, address _designatedReporterAddress) public payable returns (IMarket _newMarket) {
        return market;
    }

    function migrateMarketInFromSibling() public returns (bool) {
        return setMigrateMarketInFromSiblingValue;
    }

    function migrateMarketInFromNibling() public returns (bool) {
        return setMigrateMarketInFromNiblingValue;
    }

    function removeMarket() public returns (bool) {
        return setRemoveMarketValue;
    }

    function noteReportingGasPrice(IMarket _market) public returns (bool) {
        return setNoteReportingGasPriceValue;
    }

    function updateMarketPhase() public returns (bool) {
        return setUpdateMarketPhaseValue;
    }    

    function getUniverse() public view returns (IUniverse) {
        return universe;
    }

    function getReputationToken() public view returns (IReputationToken) {
        return setReputationTokenValue;
    }
    
    function getStartTime() public view returns (uint256) {
        return setStartTimeValue;
    }

    function getEndTime() public view returns (uint256) {
        return setEndTimeValue;
    }
    
    function getNumMarkets() public view returns (uint256) {
        return setNumMarketsValue;
    }
    
    function getNumInvalidMarkets() public view returns (uint256) {
        return setNumInvalidMarketsValue;
    }
    
    function getNumIncorrectDesignatedReportMarkets() public view returns (uint256) {
        return setNumIncorrectDesignatedReportMarketsValue;
    }
    
    function getAvgReportingGasPrice() public view returns (uint256) {
        return setAvgReportingGasPriceValue;
    }
    
    function getNextReportingWindow() public returns (IReportingWindow) {
        return setNextReportingWindowValue;
    }
    
    function getPreviousReportingWindow() public returns (IReportingWindow) {
        return setPreviousReportingWindowValue;
    }
    
    function getNumDesignatedReportNoShows() public view returns (uint256) {
        return setNumDesignatedReportNoShowsValue;
    }
    
    function allMarketsFinalized() public view returns (bool) {
        return setAllMarketsFinalizedValue;
    }
    
    function collectReportingFees(address _reporterAddress, uint256 _attoStakeTokens, bool _forgoFees) public returns (bool) {
        collectReporterAddress = _reporterAddress;
        collectAttoStakeTokens = _attoStakeTokens;
        collectForgoFees = _forgoFees;
        return true;
    }
    
    function triggerMigrateFeesDueToFork(IReportingWindow _reportingWindow) public returns (bool) {
        return setTriggerMigrateFeesDueToForkValue;
    }
    
    function migrateFeesDueToFork() public returns (bool) {
        return setMigrateFeesDueToForkValue;
    }

    function migrateFeesDueToMarketMigration(IMarket _market) public returns (bool) {
        return setMigrateFeesDueToMarketMigrationValue;
    }
    
    function isContainerForMarket(ITyped _shadyTarget) public view returns (bool) {
        return setIsContainerForMarketValue;
    }
    
    function isForkingMarketFinalized() public view returns (bool) {
        return setIsForkingMarketFinalizedValue;
    }
    
    function isDisputeActive() public view returns (bool) {
        return setIsDisputeActiveValue;
    }

    function isReportingActive() public view returns (bool) {
        return setIsReportingActiveValue;
    }

    function isActive() public view returns (bool) {
        return setIsActiveValue;
    }

    function isOver() public view returns (bool) {
        return setIsOverValue;        
    }

    function isContainerForWindowParticipationToken(ITyped _shadyTarget) public view returns (bool) {
        return setIsContainerForWindowParticipationTokenValue;
    }

    function increaseTotalStake(uint256 _amount) public returns (bool) {
        return setIncreaseTotalStakeValue;
    }
    
    function increaseTotalWinningStake(uint256 _amount) public returns (bool) {
        return setIncreaseTotalWinningStakeValue;
    }
}
