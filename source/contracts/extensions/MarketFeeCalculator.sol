pragma solidity 0.4.17;


import 'reporting/IReputationToken.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReportingWindow.sol';
import 'libraries/math/SafeMathUint256.sol';
import 'reporting/Reporting.sol';


contract MarketFeeCalculator {
    using SafeMathUint256 for uint256;

    mapping (address => uint256) private shareSettlementPerEthFee;
    mapping (address => uint256) private validityBondInAttoeth;
    mapping (address => uint256) private targetReporterGasCosts;
    mapping (address => uint256) private designatedReportStakeInAttoRep;

    uint256 private constant TARGET_INVALID_MARKETS_DIVISOR = 100; // 1% of markets are expected to be invalid
    uint256 private constant TARGET_REP_MARKET_CAP_MULTIPLIER = 5;

    uint256 private constant TARGET_INCORRECT_DESIGNATED_REPORT_MARKETS_DIVISOR = 100; // 1% of markets are expected to have an incorrect designate report

    function getValidityBond(IReportingWindow _reportingWindow) public returns (uint256) {
        uint256 _currentValidityBondInAttoeth = validityBondInAttoeth[_reportingWindow];
        if (_currentValidityBondInAttoeth != 0) {
            return _currentValidityBondInAttoeth;
        }
        IReportingWindow _previousReportingWindow = _reportingWindow.getPreviousReportingWindow();
        uint256 _totalMarketsInPreviousWindow = _previousReportingWindow.getNumMarkets();
        uint256 _invalidMarketsInPreviousWindow = _previousReportingWindow.getNumInvalidMarkets();
        uint256 _previousValidityBondInAttoeth = validityBondInAttoeth[_previousReportingWindow];

        _currentValidityBondInAttoeth = calculateFloatingValue(_invalidMarketsInPreviousWindow, _totalMarketsInPreviousWindow, TARGET_INVALID_MARKETS_DIVISOR, _previousValidityBondInAttoeth, Reporting.defaultValidityBond());
        validityBondInAttoeth[_reportingWindow] = _currentValidityBondInAttoeth;
        return _currentValidityBondInAttoeth;
    }

    function getDesignatedReportStake(IReportingWindow _reportingWindow) public returns (uint256) {
        uint256 _currentDesignatedReportStakeInAttoRep = designatedReportStakeInAttoRep[_reportingWindow];
        if (_currentDesignatedReportStakeInAttoRep != 0) {
            return _currentDesignatedReportStakeInAttoRep;
        }
        IReportingWindow _previousReportingWindow = _reportingWindow.getPreviousReportingWindow();
        uint256 _totalMarketsInPreviousWindow = _previousReportingWindow.getNumMarkets();
        uint256 _incorrectDesignatedReportMarketsInPreviousWindow = _previousReportingWindow.getNumIncorrectDesignatedReportMarkets();
        uint256 _previousDesignatedReportStakeInAttoRep = designatedReportStakeInAttoRep[_previousReportingWindow];

        _currentDesignatedReportStakeInAttoRep = calculateFloatingValue(_incorrectDesignatedReportMarketsInPreviousWindow, _totalMarketsInPreviousWindow, TARGET_INCORRECT_DESIGNATED_REPORT_MARKETS_DIVISOR, _previousDesignatedReportStakeInAttoRep, Reporting.defaultDesignatedReportStake());
        designatedReportStakeInAttoRep[_reportingWindow] = _currentDesignatedReportStakeInAttoRep;
        return _currentDesignatedReportStakeInAttoRep;
    }

    function calculateFloatingValue(uint256 _badMarkets, uint256 _totalMarkets, uint256 _targetDivisor, uint256 _previousValue, uint256 _defaultValue) public pure returns (uint256 _newValue) {
        if (_totalMarkets == 0) {
            return _defaultValue;
        }
        if (_previousValue == 0) {
            _previousValue = _defaultValue;
        }

        // Modify the amount based on the previous amount and the number of markets fitting the failure criteria. We want the amount to be somewhere in the range of 0.5 to 2 times its previous value where ALL markets with the condition results in 2x and 0 results in 0.5x.
        if (_badMarkets <= _totalMarkets.div(_targetDivisor)) {
            // FXP formula: previous_amount * actual_percent / (2 * target_percent) + 0.5;
            _newValue = _badMarkets.mul(_previousValue).mul(_targetDivisor).div(_totalMarkets).div(2).add(_previousValue.div(2)); // FIXME: This is on one line due to solium bugs
        } else {
            // FXP formula: previous_amount * (1/(1 - target_percent)) * (actual_percent - target_percent) + 1;
            _newValue = _targetDivisor.mul(_previousValue.mul(_badMarkets).div(_totalMarkets).sub(_previousValue.div(_targetDivisor))).div(_targetDivisor - 1).add(_previousValue); // FIXME: This is on one line due to a solium bug
        }

        return _newValue;
    }

    function getTargetReporterGasCosts(IReportingWindow _reportingWindow) public returns (uint256) {
        uint256 _gasToReport = targetReporterGasCosts[_reportingWindow];
        if (_gasToReport != 0) {
            return _gasToReport;
        }

        IReportingWindow _previousReportingWindow = _reportingWindow.getPreviousReportingWindow();
        uint256 _avgGasPrice = _previousReportingWindow.getAvgReportingGasPrice();
        _gasToReport = Reporting.gasToReport();
        // we double it to try and ensure we have more than enough rather than not enough
        targetReporterGasCosts[_reportingWindow] = _gasToReport * _avgGasPrice * 2;
        return targetReporterGasCosts[_reportingWindow];
    }

    function getReportingFeeInAttoethPerEth(IReportingWindow _reportingWindow) public returns (uint256) {
        // CONSIDER: store this on the reporting window rather than here
        uint256 _currentPerEthFee = shareSettlementPerEthFee[_reportingWindow];
        if (_currentPerEthFee != 0) {
            return _currentPerEthFee;
        }
        IUniverse _universe = _reportingWindow.getUniverse();
        uint256 _repMarketCapInAttoeth = getRepMarketCapInAttoeth(_universe);
        uint256 _targetRepMarketCapInAttoeth = getTargetRepMarketCapInAttoeth(_reportingWindow);
        IReportingWindow _previousReportingWindow = _reportingWindow.getPreviousReportingWindow();
        uint256 _previousPerEthFee = shareSettlementPerEthFee[_previousReportingWindow];
        if (_previousPerEthFee == 0) {
            _previousPerEthFee = 1 * 10 ** 16;
        }
        _currentPerEthFee = _previousPerEthFee * _targetRepMarketCapInAttoeth / _repMarketCapInAttoeth;
        if (_currentPerEthFee < 1 * 10 ** 14) {
            _currentPerEthFee = 1 * 10 ** 14;
        }
        shareSettlementPerEthFee[_reportingWindow] = _currentPerEthFee;
        return _currentPerEthFee;
    }

    function getRepMarketCapInAttoeth(IUniverse _universe) constant public returns (uint256) {
        // TODO: get this from a multi-sig contract that we provide and maintain
        uint256 _attorepPerEth = 11 * 10 ** 18;
        uint256 _repMarketCapInAttoeth = _universe.getReputationToken().totalSupply() * _attorepPerEth;
        return _repMarketCapInAttoeth;
    }

    function getTargetRepMarketCapInAttoeth(IReportingWindow _reportingWindow) constant public returns (uint256) {
        IUniverse _universe = _reportingWindow.getUniverse();
        return _universe.getOpenInterestInAttoEth() * TARGET_REP_MARKET_CAP_MULTIPLIER;
    }

    function getMarketCreationCost(IReportingWindow _reportingWindow) public returns (uint256) {
        return getValidityBond(_reportingWindow) + getTargetReporterGasCosts(_reportingWindow);
    }
}
