pragma solidity ^0.4.18;

import 'reporting/IMarket.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReportingWindow.sol';
import 'reporting/Reporting.sol';
import 'libraries/ITyped.sol';
import 'reporting/IReputationToken.sol';
import 'libraries/Initializable.sol';
import 'libraries/math/SafeMathUint256.sol';


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
    uint256 private setReportingPeriodDurationInSecondsValue;
    IReportingWindow private setReportingWindowByTimestampValue;
    IReportingWindow private setReportingWindowByMarketEndTimeValue;
    IReportingWindow private setCurrentReportingWindowValue;
    IReportingWindow private setNextReportingWindowValue;
    IReportingWindow private setReportingWindowForForkEndTimeValue;
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
    bool private setIsContainerForReportingWindowValue;
    bool private setIisContainerForDisputeBondValue;
    bool private setIsContainerForMarketValue;
    bool private setIsContainerForStakeTokenValue;
    bool private setIsContainerForShareTokenValue;
    bool private setIsContainerForParticipationTokenValue;
    bool private setDecrementOpenInterestValue;
    bool private setIncrementOpenInterestValue;
    IUniverse private initializParentUniverseValue;
    bytes32 private initializeParentPayoutDistributionHashValue;
    uint256 private setForkReputationGoalValue;
    /*
    * setters to feed the getters and impl of IUniverse
    */
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

    function setReportingPeriodDurationInSeconds(uint256 _setReportingPeriodDurationInSecondsValue) public {
        setReportingPeriodDurationInSecondsValue = _setReportingPeriodDurationInSecondsValue;
    }

    function setReportingWindowByTimestamp(IReportingWindow _setReportingWindowByTimestampValue) public {
        setReportingWindowByTimestampValue = _setReportingWindowByTimestampValue;
    }

    function setReportingWindowByMarketEndTime(IReportingWindow _setReportingWindowByMarketEndTimeValue) public {
        setReportingWindowByMarketEndTimeValue = _setReportingWindowByMarketEndTimeValue;
    }

    function setCurrentReportingWindow(IReportingWindow _setCurrentReportingWindowValue) public {
        setCurrentReportingWindowValue = _setCurrentReportingWindowValue;
    }

    function setNextReportingWindow(IReportingWindow _setNextReportingWindowValue) public {
        setNextReportingWindowValue = _setNextReportingWindowValue;
    }

    function setReportingWindowForForkEndTime(IReportingWindow _setReportingWindowForForkEndTimeValue) public {
        setReportingWindowForForkEndTimeValue = _setReportingWindowForForkEndTimeValue;
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

    function setValidityBond(uint256 _setValidityBondValue) public {
        setValidityBondValue = _setValidityBondValue;
    }

    function setDesignatedReportStake(uint256 _setDesignatedReportStakeValue) public {
        setDesignatedReportStakeValue = _setDesignatedReportStakeValue;
    }

    function setDesignatedReportNoShowBond(uint256 _setDesignatedReportNoShowBondValue) public {
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

    function setTargetReporterGasCosts(uint256 _setTargetReporterGasCostsValue) public {
        setTargetReporterGasCostsValue = _setTargetReporterGasCostsValue;
    }

    function setMarketCreationCost(uint256 _setMarketCreationCostValue) public {
        setMarketCreationCostValue = _setMarketCreationCostValue;
    }

    function setIsParentOf(bool _setIsParentOfValue) public {
        setIsParentOfValue = _setIsParentOfValue;
    }

    function setIsContainerForReportingWindow(bool _setIsContainerForReportingWindowValue) public {
        setIsContainerForReportingWindowValue = _setIsContainerForReportingWindowValue;
    }

    function setIsContainerForDisputeBond(bool _setIisContainerForDisputeBondValue) public {
        setIisContainerForDisputeBondValue = _setIisContainerForDisputeBondValue;
    }

    function setIsContainerForMarket(bool _setIsContainerForMarketValue) public {
        setIsContainerForMarketValue = _setIsContainerForMarketValue;
    }

    function setIsContainerForStakeToken(bool _setIsContainerForStakeTokenValue) public {
        setIsContainerForStakeTokenValue = _setIsContainerForStakeTokenValue;
    }

    function setIsContainerForShareToken(bool _setIsContainerForShareTokenValue) public {
        setIsContainerForShareTokenValue = _setIsContainerForShareTokenValue;
    }

    function setIsContainerForParticipationToken(bool _setIsContainerForParticipationTokenValue) public {
        setIsContainerForParticipationTokenValue = _setIsContainerForParticipationTokenValue;
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

    function getReportingPeriodDurationInSeconds() public view returns (uint256) {
        return setReportingPeriodDurationInSecondsValue;
    }

    function getOrCreateReportingWindowByTimestamp(uint256 _timestamp) public returns (IReportingWindow) {
        return setReportingWindowByTimestampValue;
    }

    function getOrCreateReportingWindowByMarketEndTime(uint256 _endTime) public returns (IReportingWindow) {
        return setReportingWindowByMarketEndTimeValue;
    }

    function getOrCreateCurrentReportingWindow() public returns (IReportingWindow) {
        return setCurrentReportingWindowValue;
    }

    function getOrCreateNextReportingWindow() public returns (IReportingWindow) {
        return setNextReportingWindowValue;
    }

    function getOrCreateReportingWindowForForkEndTime() public returns (IReportingWindow) {
        return setReportingWindowForForkEndTimeValue;
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

    function getOrCacheValidityBond() public returns (uint256) {
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

    function getOrCacheTargetReporterGasCosts() public returns (uint256) {
        return setTargetReporterGasCostsValue;
    }

    function getOrCacheMarketCreationCost() public returns (uint256) {
        return setMarketCreationCostValue;
    }

    function isParentOf(IUniverse _shadyChild) public view returns (bool) {
        return setIsParentOfValue;
    }

    function isContainerForReportingWindow(IReportingWindow _shadyTarget) public view returns (bool) {
        return setIsContainerForReportingWindowValue;
    }

    function isContainerForDisputeBond(IDisputeBond _shadyTarget) public view returns (bool) {
        return setIisContainerForDisputeBondValue;
    }

    function isContainerForMarket(IMarket _shadyTarget) public view returns (bool) {
        return setIsContainerForMarketValue;
    }

    function isContainerForStakeToken(IStakeToken _shadyTarget) public view returns (bool) {
        return setIsContainerForStakeTokenValue;
    }

    function isContainerForShareToken(IShareToken _shadyTarget) public view returns (bool) {
        return setIsContainerForShareTokenValue;
    }

    function isContainerForParticipationToken(IParticipationToken _shadyTarget) public view returns (bool) {
        return setIsContainerForParticipationTokenValue;
    }

    function decrementOpenInterest(uint256 _amount) public returns (bool) {
        return setDecrementOpenInterestValue;
    }

    function incrementOpenInterest(uint256 _amount) public returns (bool) {
        return setIncrementOpenInterestValue;
    }

    function getForkReputationGoal() public view returns (uint256) {
        return setForkReputationGoalValue;
    }

    function createBinaryMarket(uint256 _endTime, uint256 _feePerEthInWei, ICash _denominationToken, address _designatedReporterAddress, bytes32 _topic, bytes32 _description, string _extraInfo) public payable returns (IMarket _newMarket) {
        IReportingWindow _reportingWindow = getOrCreateReportingWindowByMarketEndTime(_endTime);
        _newMarket = _reportingWindow.createMarket.value(msg.value)(_endTime, _feePerEthInWei, _denominationToken, _designatedReporterAddress, msg.sender, 2, Reporting.getBinaryMarketNumTicks());
        return _newMarket;
    }

    function createCategoricalMarket(uint256 _endTime, uint256 _feePerEthInWei, ICash _denominationToken, address _designatedReporterAddress, uint8 _numOutcomes, bytes32 _topic, bytes32 _description, string _extraInfo) public payable returns (IMarket _newMarket) {
        IReportingWindow _reportingWindow = getOrCreateReportingWindowByMarketEndTime(_endTime);
        _newMarket = _reportingWindow.createMarket.value(msg.value)(_endTime, _feePerEthInWei, _denominationToken, _designatedReporterAddress, msg.sender, _numOutcomes, Reporting.getCategoricalMarketNumTicks(_numOutcomes));
        return _newMarket;
    }

    function createScalarMarket(uint256 _endTime, int256 _minPrice, int256 _maxPrice, uint256 _normalizedTicks, uint256 _feePerEthInWei, ICash _denominationToken, address _designatedReporterAddress, bytes32 _topic, bytes32 _description, string _extraInfo) public payable returns (IMarket _newMarket) {
        IReportingWindow _reportingWindow = getOrCreateReportingWindowByMarketEndTime(_endTime);
        uint256 _numTicks = (uint256 (_maxPrice - _minPrice)).mul(_normalizedTicks);
        _newMarket = _reportingWindow.createMarket.value(msg.value)(_endTime, _feePerEthInWei, _denominationToken, _designatedReporterAddress, msg.sender, 2, _numTicks);
        return _newMarket;
    }
}
