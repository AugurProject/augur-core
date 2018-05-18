pragma solidity ^0.4.20;

import 'reporting/IMarket.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IFeeWindow.sol';
import 'IController.sol';
import 'libraries/ITyped.sol';
import 'reporting/IReputationToken.sol';
import 'libraries/Initializable.sol';
import 'TEST/MockVariableSupplyToken.sol';


contract MockFeeWindow is Initializable, MockVariableSupplyToken, IFeeWindow {
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
    IFeeWindow private setNextFeeWindowValue;
    IFeeWindow private setPreviousFeeWindowValue;
    uint256 private setNumDesignatedReportNoShowsValue;
    bool private setAllMarketsFinalizedValue;
    uint256 private setCollectFeeWindowReportingFeesValue;
    bool private setMigrateFeesDueToForkValue;
    bool private setIsContainerForMarketValue;
    bool private setIsForkingMarketFinalizedValue;
    bool private setIsDisputeActiveValue;
    IMarket private market;
    IUniverse private initializeUniverseValue;
    uint256 private initializeFeeWindowIdValue;
    address private collectReporterAddress;
    bool private collectForgoFees;
    bool private setIsReportingActiveValue;
    bool private setIsActiveValue;
    bool private setIsOverValue;
    bool private setIsContainerForFeeWindowValue;
    bool private setIncreaseTotalStakeValue;
    bool private setIncreaseTotalWinningStakeValue;
    bool private setNoteDesignatedReportValue;

    /*
    * setters to feed the getters and impl of IFeeWindow
    */
    function reset() public {
        setUpdateMarketPhaseValue = false;
        setNoteDesignatedReportValue = false;
        setIncreaseTotalStakeValue = false;
        setRemoveMarketValue = false;
        setMigrateMarketInFromSiblingValue = false;
        setMigrateMarketInFromNiblingValue = false;
    }

    function getMigrateMarketInFromSiblingCalled() public returns(bool) {
        return setMigrateMarketInFromSiblingValue;
    }

    function getMigrateMarketInFromNiblingCalled() public returns(bool) {
        return setMigrateMarketInFromNiblingValue;
    }

    function getRemoveMarketCalled() public returns (bool) {
        return setRemoveMarketValue;
    }

    function setNoteReportingGasPrice(bool _setNoteReportingGasPriceValue) public {
        setNoteReportingGasPriceValue = _setNoteReportingGasPriceValue;
    }

    function getUpdateMarketPhaseCalled() public returns(bool) {
        return setUpdateMarketPhaseValue;
    }

    function getNoteDesignatedReport() public returns(bool) {
        return setNoteDesignatedReportValue;
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

    function setNextFeeWindow(IFeeWindow _setNextFeeWindowValue) public {
        setNextFeeWindowValue = _setNextFeeWindowValue;
    }

    function setPreviousFeeWindow(IFeeWindow _setPreviousFeeWindowValue) public {
        setPreviousFeeWindowValue = _setPreviousFeeWindowValue;
    }

    function setNumDesignatedReportNoShows(uint256 _setNumDesignatedReportNoShowsValue) public {
        setNumDesignatedReportNoShowsValue = _setNumDesignatedReportNoShowsValue;
    }

    function setAllMarketsFinalized(bool _setAllMarketsFinalizedValue) public {
        setAllMarketsFinalizedValue = _setAllMarketsFinalizedValue;
    }

    function setCollectFeeWindowReportingFees(uint256 _setCollectFeeWindowReportingFeesValue) public {
        setCollectFeeWindowReportingFeesValue = _setCollectFeeWindowReportingFeesValue;
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

    function setIsContainerForFeeWindow(bool _isContainerForFeeWindow) public {
        setIsContainerForFeeWindowValue = _isContainerForFeeWindow;
    }

    function getIncreaseTotalStakeCalled() public returns(bool) {
        return setIncreaseTotalStakeValue;
    }

    function setIncreaseTotalWinningStake(bool _setIncreaseTotalWinningStakeValue) public {
        setIncreaseTotalWinningStakeValue = _setIncreaseTotalWinningStakeValue;
    }

    function getInitializeUniverseValue() public view returns(IUniverse) {
        return initializeUniverseValue;
    }

    function getinitializeFeeWindowIdValue() public returns(uint256) {
        return initializeFeeWindowIdValue;
    }

    function getCollectReporterAddress() public returns(address) {
        return collectReporterAddress;
    }

    function callTrustedFeeWindowTransfer(IReputationToken _reputationToken, address _source, address _destination, uint256 _attotokens) public returns (bool) {
        return _reputationToken.trustedFeeWindowTransfer(_source, _destination, _attotokens);
    }

    /*
    * Impl of IFeeWindow and ITyped
     */
    function getTypeName() public afterInitialized view returns (bytes32) {
        return "FeeWindow";
    }

    function initialize(IUniverse _universe, uint256 _feeWindowId) public returns (bool) {
        endInitialization();
        initializeUniverseValue = _universe;
        initializeFeeWindowIdValue = _feeWindowId;
        return true;
    }

    function createMarket(uint256 _endTime, uint256 _feePerEthInWei, ICash _denominationToken, address _designatedReporterAddress, address _sender, uint256 _numOutcomes, uint256 _numTicks) public payable returns (IMarket _newMarket) {
        return market;
    }

    function migrateMarketInFromSibling() public returns (bool) {
        setMigrateMarketInFromSiblingValue = true;
        return true;
    }

    function migrateMarketInFromNibling() public returns (bool) {
        setMigrateMarketInFromNiblingValue = true;
        return true;
    }

    function removeMarket() public returns (bool) {
        setRemoveMarketValue = true;
        return true;
    }

    function noteReportingGasPrice(IMarket _market) public returns (bool) {
        return setNoteReportingGasPriceValue;
    }

    function noteDesignatedReport() public returns (bool) {
        setNoteDesignatedReportValue = true;
        return true;
    }

    function updateMarketPhase() public returns (bool) {
        setUpdateMarketPhaseValue = true;
        return true;
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

    function getOrCreateNextFeeWindow() public returns (IFeeWindow) {
        return setNextFeeWindowValue;
    }

    function getOrCreatePreviousFeeWindow() public returns (IFeeWindow) {
        return setPreviousFeeWindowValue;
    }

    function getNumDesignatedReportNoShows() public view returns (uint256) {
        return setNumDesignatedReportNoShowsValue;
    }

    function allMarketsFinalized() public view returns (bool) {
        return setAllMarketsFinalizedValue;
    }

    function migrateFeesDueToFork() public returns (bool) {
        return setMigrateFeesDueToForkValue;
    }

    function isContainerForMarket(IMarket _shadyTarget) public view returns (bool) {
        return setIsContainerForMarketValue;
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

    function isContainerForFeeWindow(IFeeWindow _shadyTarget) public view returns (bool) {
        return setIsContainerForFeeWindowValue;
    }

    function increaseTotalStake(uint256 _amount) public returns (bool) {
        setIncreaseTotalStakeValue = true;
    }

    function increaseTotalWinningStake(uint256 _amount) public returns (bool) {
        return setIncreaseTotalWinningStakeValue;
    }

    function noteInitialReportingGasPrice() public returns (bool) {
        return true;
    }

    function onMarketFinalized() public returns (bool) {
        return true;
    }

    function buy(uint256 _attotokens) public returns (bool) {
        return true;
    }

    function redeem(address _sender) public returns (bool) {
        return true;
    }

    function onTokenTransfer(address _from, address _to, uint256 _value) internal returns (bool) {
        return true;
    }

    function onMint(address _target, uint256 _amount) internal returns (bool) {
        return true;
    }

    function onBurn(address _target, uint256 _amount) internal returns (bool) {
        return true;
    }

    function getFeeToken() public view returns (IFeeToken) {
        return IFeeToken(0);
    }

    function redeemForReportingParticipant() public returns (bool) {
        return true;
    }

    function mintFeeTokens(uint256 _amount) public returns (bool) {
        return true;
    }

    function getController() public view returns (IController) {
        return IController(0);
    }

    function setController(IController _controller) public returns(bool) {
        return true;
    }

    function suicideFunds(address _target, ERC20Basic[] _tokens) public returns(bool) {
        return true;
    }

    function trustedUniverseBuy(address _buyer, uint256 _attotokens) public returns (bool) {
        return true;
    }
}
