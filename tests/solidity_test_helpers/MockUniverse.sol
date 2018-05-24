pragma solidity ^0.4.20;

import 'reporting/IMarket.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IFeeWindow.sol';
import 'reporting/Reporting.sol';
import 'libraries/ITyped.sol';
import 'reporting/IReputationToken.sol';
import 'libraries/Initializable.sol';
import 'libraries/math/SafeMathUint256.sol';
import 'factories/MarketFactory.sol';
import 'Controller.sol';


contract MockUniverse is Initializable, IUniverse {
    using SafeMathUint256 for uint256;

    bool private setforkValue;
    IUniverse private setParentUniverseValue;
    IUniverse private setOrCreateChildUniverseValue;
    IUniverse private setChildUniverseValue;
    IReputationToken private setReputationTokenValue;
    IMarket private setForkingMarketValue;
    uint256 private setForkEndTimeValue;
    bytes32 private setParentPayoutDistributionHashValue;
    uint256 private setDisputeRoundDurationInSecondsValue;
    IFeeWindow private setFeeWindowByTimestampValue;
    IFeeWindow private setFeeWindowByMarketEndTimeValue;
    IFeeWindow private setCurrentFeeWindowValue;
    IFeeWindow private setNextFeeWindowValue;
    IFeeWindow private setFeeWindowForForkEndTimeValue;
    uint256 private setOpenInterestInAttoEthValue;
    uint256 private setRepMarketCapInAttoethValue;
    uint256 private setTargetRepMarketCapInAttoethValue;
    uint256 private setValidityBondValue;
    uint256 private setDesignatedReportStakeValue;
    uint256 private setDesignatedReportNoShowBondValue;
    uint256 private setReportingFeeDivisorValue;
    uint256 private setRepAvailableForExtraBondPayoutsValue;
    bool private setIncreaseRepAvailableForExtraBondPayoutsValue;
    bool private setDecreaseRepAvailableForExtraBondPayoutsValue;
    uint256 private setCalculateFloatingValueValue;
    uint256 private setTargetReporterGasCostsValue;
    uint256 private setMarketCreationCostValue;
    bool private setIsParentOfValue;
    bool private setIsContainerForFeeWindowValue;
    bool private setIsContainerForMarketValue;
    bool private setIsContainerForShareTokenValue;
    bool private setDecrementOpenInterestValue;
    bool private setIncrementOpenInterestValue;
    IUniverse private initializParentUniverseValue;
    bytes32 private initializeParentPayoutDistributionHashValue;
    uint256 private setForkReputationGoalValue;
    MarketFactory private marketFactory;
    Controller private controller;
    bool private setIsContainerForReportingParticipantValue;
    bool private setIsForkingValue;
    bool private getOrCacheValidityBondWallCalledValue;
    bool private getOrCacheTargetReporterGasCostsWasCalledValue;
    uint256 private setDisputeThresholdForForkValue;
    bool private getOrCreateNextFeeWindowWasCalledValue;
    IUniverse private setWinningChildUniverseValue;
    bool private addMarketToWasCalledValue;
    bool private removeMarketFromWasCalledValue;
    /*
    * setters to feed the getters and impl of IUniverse
    */
    function reset() public {
        setforkValue = false;
        getOrCreateNextFeeWindowWasCalledValue = false;
        addMarketToWasCalledValue = false;
        removeMarketFromWasCalledValue = false;
    }

    function getForkCalled() public returns(bool) {
        return setforkValue;
    }

    function setParentUniverse(IUniverse _setParentUniverseValue) public {
        setParentUniverseValue = _setParentUniverseValue;
    }

    function setOrCreateChildUniverse(IUniverse _setOrCreateChildUniverseValue) public {
        setOrCreateChildUniverseValue = _setOrCreateChildUniverseValue;
    }

    function setChildUniverse(IUniverse _setChildUniverseValue) public {
        setChildUniverseValue = _setChildUniverseValue;
    }

    function setReputationToken(IReputationToken _setReputationTokenValue) public {
        setReputationTokenValue = _setReputationTokenValue;
    }

    function setForkingMarket(IMarket _setForkingMarketValue) public {
        setForkingMarketValue = _setForkingMarketValue;
    }

    function setForkEndTime(uint256 _setForkEndTimeValue) public {
        setForkEndTimeValue = _setForkEndTimeValue;
    }

    function setParentPayoutDistributionHash(bytes32 _setParentPayoutDistributionHashValue) public {
        setParentPayoutDistributionHashValue = _setParentPayoutDistributionHashValue;
    }

    function setDisputeRoundDurationInSeconds(uint256 _setDisputeRoundDurationInSecondsValue) public {
        setDisputeRoundDurationInSecondsValue = _setDisputeRoundDurationInSecondsValue;
    }

    function setFeeWindowByTimestamp(IFeeWindow _setFeeWindowByTimestampValue) public {
        setFeeWindowByTimestampValue = _setFeeWindowByTimestampValue;
    }

    function setFeeWindowByMarketEndTime(IFeeWindow _setFeeWindowByMarketEndTimeValue) public {
        setFeeWindowByMarketEndTimeValue = _setFeeWindowByMarketEndTimeValue;
    }

    function setCurrentFeeWindow(IFeeWindow _setCurrentFeeWindowValue) public {
        setCurrentFeeWindowValue = _setCurrentFeeWindowValue;
    }

    function setNextFeeWindow(IFeeWindow _setNextFeeWindowValue) public {
        setNextFeeWindowValue = _setNextFeeWindowValue;
    }

    function setFeeWindowForForkEndTime(IFeeWindow _setFeeWindowForForkEndTimeValue) public {
        setFeeWindowForForkEndTimeValue = _setFeeWindowForForkEndTimeValue;
    }

    function setOpenInterestInAttoEth(uint256 _setOpenInterestInAttoEthValue) public {
        setOpenInterestInAttoEthValue = _setOpenInterestInAttoEthValue;
    }

    function setRepMarketCapInAttoeth(uint256 _setRepMarketCapInAttoethValue) public {
        setRepMarketCapInAttoethValue = _setRepMarketCapInAttoethValue;
    }

    function setTargetRepMarketCapInAttoeth(uint256 _setTargetRepMarketCapInAttoethValue) public {
        setTargetRepMarketCapInAttoethValue = _setTargetRepMarketCapInAttoethValue;
    }

    function setOrCacheValidityBond(uint256 _setValidityBondValue) public {
        setValidityBondValue = _setValidityBondValue;
    }

    function setOrCacheDesignatedReportStake(uint256 _setDesignatedReportStakeValue) public {
        setDesignatedReportStakeValue = _setDesignatedReportStakeValue;
    }

    function setOrCacheDesignatedReportNoShowBond(uint256 _setDesignatedReportNoShowBondValue) public {
        setDesignatedReportNoShowBondValue = _setDesignatedReportNoShowBondValue;
    }

    function setReportingFeeDivisor(uint256 _setReportingFeeDivisorValue) public {
        setReportingFeeDivisorValue = _setReportingFeeDivisorValue;
    }

    function setRepAvailableForExtraBondPayouts(uint256 _setRepAvailableForExtraBondPayoutsValue) public {
        setRepAvailableForExtraBondPayoutsValue = _setRepAvailableForExtraBondPayoutsValue;
    }

    function setIncreaseRepAvailableForExtraBondPayouts(bool _setIncreaseRepAvailableForExtraBondPayoutsValue) public {
        setIncreaseRepAvailableForExtraBondPayoutsValue = _setIncreaseRepAvailableForExtraBondPayoutsValue;
    }

    function setDecreaseRepAvailableForExtraBondPayouts(bool _setDecreaseRepAvailableForExtraBondPayoutsValue) public {
        setDecreaseRepAvailableForExtraBondPayoutsValue = _setDecreaseRepAvailableForExtraBondPayoutsValue;
    }

    function setCalculateFloatingValue(uint256 _setCalculateFloatingValueValue) public {
        setCalculateFloatingValueValue = _setCalculateFloatingValueValue;
    }

    function setOrCacheTargetReporterGasCosts(uint256 _setTargetReporterGasCostsValue) public {
        setTargetReporterGasCostsValue = _setTargetReporterGasCostsValue;
    }

    function setMarketCreationCost(uint256 _setMarketCreationCostValue) public {
        setMarketCreationCostValue = _setMarketCreationCostValue;
    }

    function setIsParentOf(bool _setIsParentOfValue) public {
        setIsParentOfValue = _setIsParentOfValue;
    }

    function setIsContainerForMarket(bool _setIsContainerForMarketValue) public {
        setIsContainerForMarketValue = _setIsContainerForMarketValue;
    }

    function setIsContainerForShareToken(bool _setIsContainerForShareTokenValue) public {
        setIsContainerForShareTokenValue = _setIsContainerForShareTokenValue;
    }

    function setIsContainerForFeeWindow(bool _setIsContainerForFeeWindowValue) public {
        setIsContainerForFeeWindowValue = _setIsContainerForFeeWindowValue;
    }

    function setDecrementOpenInterest(bool _setDecrementOpenInterestValue) public {
        setDecrementOpenInterestValue = _setDecrementOpenInterestValue;
    }

    function setIncrementOpenInterest(bool _setIncrementOpenInterestValue) public {
        setIncrementOpenInterestValue = _setIncrementOpenInterestValue;
    }

    function setForkReputationGoal(uint256 _forkReputationGoalValue) public {
        setForkReputationGoalValue = _forkReputationGoalValue;
    }

    function getInitializParentUniverseValue() public view returns (IUniverse) {
        return initializParentUniverseValue;
    }

    function getInitializeParentPayoutDistributionHashValue() public returns (bytes32) {
        return initializeParentPayoutDistributionHashValue;
    }

    function setIsContainerForReportingParticipant(bool _value) public {
        setIsContainerForReportingParticipantValue = _value;
    }

    /*
    * Impl of IUniverse and ITyped
     */
    function getTypeName() public view returns (bytes32) {
        return "Universe";
    }

    function initialize(IUniverse _parentUniverse, bytes32 _parentPayoutDistributionHash) external returns (bool) {
        initializParentUniverseValue = _parentUniverse;
        initializeParentPayoutDistributionHashValue = _parentPayoutDistributionHash;
        return true;
    }

    function fork() public returns (bool) {
        setforkValue = true;
        return true;
    }

    function getParentUniverse() public view returns (IUniverse) {
        return setParentUniverseValue;
    }

    function getOrCreateChildUniverse(bytes32 _parentPayoutDistributionHash) public returns (IUniverse) {
        return setOrCreateChildUniverseValue;
    }

    function getChildUniverse(bytes32 _parentPayoutDistributionHash) public view returns (IUniverse) {
        return setChildUniverseValue;
    }

    function getReputationToken() public view returns (IReputationToken) {
        return setReputationTokenValue;
    }

    function getForkingMarket() public view returns (IMarket) {
        return setForkingMarketValue;
    }

    function getForkEndTime() public view returns (uint256) {
        return setForkEndTimeValue;
    }

    function getParentPayoutDistributionHash() public view returns (bytes32) {
        return setParentPayoutDistributionHashValue;
    }

    function getDisputeRoundDurationInSeconds() public view returns (uint256) {
        return setDisputeRoundDurationInSecondsValue;
    }

    function getOrCreateFeeWindowByTimestamp(uint256 _timestamp) public returns (IFeeWindow) {
        return setFeeWindowByTimestampValue;
    }

    function getOrCreateFeeWindowByMarketEndTime(uint256 _endTime) public returns (IFeeWindow) {
        return setFeeWindowByMarketEndTimeValue;
    }

    function getOrCreateCurrentFeeWindow() public returns (IFeeWindow) {
        return setCurrentFeeWindowValue;
    }

    function getOrCreateNextFeeWindowWasCalled() public returns(bool) { return getOrCreateNextFeeWindowWasCalledValue;}

    function getOrCreateNextFeeWindow() public returns (IFeeWindow) {
        getOrCreateNextFeeWindowWasCalledValue = true;
        return setNextFeeWindowValue;
    }

    function getOrCreateFeeWindowForForkEndTime() public returns (IFeeWindow) {
        return setFeeWindowForForkEndTimeValue;
    }

    function getOpenInterestInAttoEth() public view returns (uint256) {
        return setOpenInterestInAttoEthValue;
    }

    function getRepMarketCapInAttoeth() public view returns (uint256) {
        return setRepMarketCapInAttoethValue;
    }

    function getTargetRepMarketCapInAttoeth() public view returns (uint256) {
        return setTargetRepMarketCapInAttoethValue;
    }

    function getOrCacheValidityBondWallCalled() public returns(bool) { return getOrCacheValidityBondWallCalledValue; }

    function getOrCacheValidityBond() public returns (uint256) {
        getOrCacheValidityBondWallCalledValue = true;
        return setValidityBondValue;
    }

    function getOrCacheDesignatedReportStake() public returns (uint256) {
        return setDesignatedReportStakeValue;
    }

    function getOrCacheDesignatedReportNoShowBond() public returns (uint256) {
        return setDesignatedReportNoShowBondValue;
    }

    function getOrCacheReportingFeeDivisor() public returns (uint256) {
        return setReportingFeeDivisorValue;
    }

    function getRepAvailableForExtraBondPayouts() public view returns (uint256) {
        return setRepAvailableForExtraBondPayoutsValue;
    }

    function increaseRepAvailableForExtraBondPayouts(uint256 _amount) public returns (bool) {
        return setIncreaseRepAvailableForExtraBondPayoutsValue;
    }

    function decreaseRepAvailableForExtraBondPayouts(uint256 _amount) public returns (bool) {
        return setDecreaseRepAvailableForExtraBondPayoutsValue;
    }

    function calculateFloatingValue(uint256 _badMarkets, uint256 _totalMarkets, uint256 _targetDivisor, uint256 _previousValue, uint256 _defaultValue, uint256 _floor) public pure returns (uint256 _newValue) {
        if (_totalMarkets == 0) {
            return _defaultValue;
        }
        if (_previousValue == 0) {
            _previousValue = _defaultValue;
        }

        // Modify the amount based on the previous amount and the number of markets fitting the failure criteria. We want the amount to be somewhere in the range of 0.5 to 2 times its previous value where ALL markets with the condition results in 2x and 0 results in 0.5x.
        if (_badMarkets <= _totalMarkets / _targetDivisor) {
            // FXP formula: previous_amount * actual_percent / (2 * target_percent) + 0.5;
            _newValue = _badMarkets.mul(_previousValue).mul(_targetDivisor).div(_totalMarkets).div(2)  + _previousValue / 2; // FIXME: This is on one line due to solium bugs
        } else {
            // FXP formula: previous_amount * (1/(1 - target_percent)) * (actual_percent - target_percent) + 1;
            _newValue = _targetDivisor.mul(_previousValue.mul(_badMarkets).div(_totalMarkets).sub(_previousValue.div(_targetDivisor))).div(_targetDivisor - 1) + _previousValue; // FIXME: This is on one line due to a solium bug
        }

        if (_newValue < _floor) {
            _newValue = _floor;
        }

        return _newValue;
    }

    function getOrCacheTargetReporterGasCostsWasCalled() public returns(bool) { return getOrCacheTargetReporterGasCostsWasCalledValue; }

    function getOrCacheTargetReporterGasCosts() public returns (uint256) {
        getOrCacheTargetReporterGasCostsWasCalledValue = true;
        return setTargetReporterGasCostsValue;
    }

    function getOrCacheMarketCreationCost() public returns (uint256) {
        return setMarketCreationCostValue;
    }

    function isParentOf(IUniverse _shadyChild) public view returns (bool) {
        return setIsParentOfValue;
    }

    function isContainerForMarket(IMarket _shadyTarget) public view returns (bool) {
        return setIsContainerForMarketValue;
    }

    function isContainerForShareToken(IShareToken _shadyTarget) public view returns (bool) {
        return setIsContainerForShareTokenValue;
    }

    function isContainerForFeeWindow(IFeeWindow _shadyTarget) public view returns (bool) {
        return setIsContainerForFeeWindowValue;
    }

    function decrementOpenInterest(uint256 _amount) public returns (bool) {
        return setDecrementOpenInterestValue;
    }

    function incrementOpenInterest(uint256 _amount) public returns (bool) {
        return setIncrementOpenInterestValue;
    }

    function incrementOpenInterestFromMarket(uint256 _amount) public returns (bool) {
        return true;
    }

    function decrementOpenInterestFromMarket(uint256 _amount) public returns (bool) {
        return true;
    }

    function getForkReputationGoal() public view returns (uint256) {
        return setForkReputationGoalValue;
    }

    function createBinaryMarket(uint256 _endTime, uint256 _feePerEthInWei, ICash _denominationToken, address _designatedReporterAddress, bytes32 _topic, string _description, string _extraInfo) public payable returns (IMarket _newMarket) {
        _newMarket = createMarketInternal(_endTime, _feePerEthInWei, _denominationToken, _designatedReporterAddress, msg.sender, 2, 10000);
        return _newMarket;
    }

    function createCategoricalMarket(uint256 _endTime, uint256 _feePerEthInWei, ICash _denominationToken, address _designatedReporterAddress, bytes32[] _outcomes, bytes32 _topic, string _description, string _extraInfo) public payable returns (IMarket _newMarket) {
        _newMarket = createMarketInternal(_endTime, _feePerEthInWei, _denominationToken, _designatedReporterAddress, msg.sender, uint256(_outcomes.length), 10000);
        return _newMarket;
    }

    function createScalarMarket(uint256 _endTime, uint256 _feePerEthInWei, ICash _denominationToken, address _designatedReporterAddress, int256 _minPrice, int256 _maxPrice, uint256 _numTicks, bytes32 _topic, string _description, string _extraInfo) public payable returns (IMarket _newMarket) {
        _newMarket = createMarketInternal(_endTime, _feePerEthInWei, _denominationToken, _designatedReporterAddress, msg.sender, 2, _numTicks);
        return _newMarket;
    }

    function createMarketInternal(uint256 _endTime, uint256 _feePerEthInWei, ICash _denominationToken, address _designatedReporterAddress, address _sender, uint256 _numOutcomes, uint256 _numTicks) private returns (IMarket _newMarket) {
        getReputationToken().trustedUniverseTransfer(_sender, marketFactory, getOrCacheDesignatedReportNoShowBond());
        _newMarket = marketFactory.createMarket.value(msg.value)(controller, this, _endTime, _feePerEthInWei, _denominationToken, _designatedReporterAddress, _sender, _numOutcomes, _numTicks);
        return _newMarket;
    }

    function createChildUniverse(uint256[] _parentPayoutNumerators, bool _parentInvalid) public returns (IUniverse) {
        return IUniverse(0);
    }

    function isContainerForReportingParticipant(IReportingParticipant _reportingParticipant) public view returns (bool) {
        return setIsContainerForReportingParticipantValue;
    }

    function addMarketToWasCalled() public returns(bool) { return addMarketToWasCalledValue; }

    function addMarketTo() public returns (bool) {
        addMarketToWasCalledValue = true;
        return true;
    }

    function removeMarketFromWasCalled() public returns(bool) { return removeMarketFromWasCalledValue; }

    function removeMarketFrom() public returns (bool) {
        removeMarketFromWasCalledValue = true;
        return true;
    }

    function setWinningChildUniverse(IUniverse _winning) public {
        setWinningChildUniverseValue = _winning;
    }

    function getWinningChildUniverse() public view returns (IUniverse) {
        return setWinningChildUniverseValue;
    }

    function getCurrentFeeWindow() public view returns (IFeeWindow) {
        return IFeeWindow(0);
    }

    function getOrCreateFeeWindowBefore(IFeeWindow _feeWindow) public returns (IFeeWindow) {
        return IFeeWindow(0);
    }

    function isContainerForFeeToken(IFeeToken _shadyTarget) public view returns (bool) {
        return true;
    }

    function setIsForking(bool _isForking) public { setIsForkingValue = _isForking; }

    function isForking() public view returns (bool) {
        return setIsForkingValue;
    }

    function updateTentativeWinningChildUniverse(bytes32 _parentPayoutDistributionHash) public returns (bool) {
        return true;
    }

    function setDisputeThresholdForFork(uint256 _value) public { setDisputeThresholdForForkValue = _value; }

    function getDisputeThresholdForFork() public view returns (uint256) {
        return setDisputeThresholdForForkValue;
    }

    function getInitialReportMinValue() public view returns (uint256) {
        return 0;
    }
}
