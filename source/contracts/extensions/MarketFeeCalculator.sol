pragma solidity ^0.4.13;

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

    uint256 private constant DEFAULT_VALIDITY_BOND = 1 ether / 100;
    uint256 private constant TARGET_INVALID_MARKETS_DIVISOR = 100; // 1% of markets
    uint256 private constant TARGET_REP_MARKET_CAP_MULTIPLIER = 5;

    function getValidityBond(IReportingWindow _reportingWindow) public returns (uint256) {
        uint256 _currentValidityBondInAttoeth = validityBondInAttoeth[_reportingWindow];
        if (_currentValidityBondInAttoeth != 0) {
            return _currentValidityBondInAttoeth;
        }
        IReportingWindow _previousReportingWindow = _reportingWindow.getPreviousReportingWindow();
        uint256 _totalMarketsInPreviousWindow = _reportingWindow.getNumMarkets();
        uint256 _invalidMarketsInPreviousWindow = _reportingWindow.getNumInvalidMarkets();
        uint256 _previousValidityBondInAttoeth = validityBondInAttoeth[_previousReportingWindow];

        _currentValidityBondInAttoeth = calculateValidityBond(_invalidMarketsInPreviousWindow, _totalMarketsInPreviousWindow, TARGET_INVALID_MARKETS_DIVISOR, _previousValidityBondInAttoeth);
        validityBondInAttoeth[_reportingWindow] = _currentValidityBondInAttoeth;
        return _currentValidityBondInAttoeth;
    }

    function calculateValidityBond(uint256 _invalidMarkets, uint256 _totalMarkets, uint256 _targetInvalidMarketsDivisor, uint256 _previousValidityBondInAttoeth) constant public returns (uint256) {
        if (_totalMarkets == 0) {
            return DEFAULT_VALIDITY_BOND;
        }
        if (_previousValidityBondInAttoeth == 0) {
            _previousValidityBondInAttoeth = DEFAULT_VALIDITY_BOND;
        }
        
        uint256 _targetInvalidMarkets = _totalMarkets.div(_targetInvalidMarketsDivisor);

        // Modify the validity bond based on the previous amount and the number of invalid markets. We want the bond to be somewhere in the range of 0.5 to 2 times its previous value where ALL markets being invalid results in 2x and 0 invalid results in 0.5x.
        if (_invalidMarkets <= _targetInvalidMarkets) {
            // FXP formula: previous_bond * percent_invalid / (2 * target_percent_invalid) + 0.5;
            return _invalidMarkets
                .mul(_previousValidityBondInAttoeth)
                .mul(_targetInvalidMarketsDivisor)
                .div(_totalMarkets)
                .div(2)
                .add(_previousValidityBondInAttoeth.div(2))
            ; // FIXME: This is here due to a solium bug
        } else {
            // FXP formula: previous_bond * (1/(1 - target_percent_invalid)) * (percent_invalid - target_percent_invalid) + 1;
            return _targetInvalidMarketsDivisor
                .mul(_previousValidityBondInAttoeth.mul(_invalidMarkets)
                .div(_totalMarkets)
                .sub(_previousValidityBondInAttoeth.div(_targetInvalidMarketsDivisor)))
                .div(_targetInvalidMarketsDivisor - 1)
                .add(_previousValidityBondInAttoeth)
            ; // FIXME: This is here due to a solium bug
        }
    }

    function getTargetReporterGasCosts(IReportingWindow _reportingWindow) constant public returns (uint256) {
        uint256 _gasToReport = targetReporterGasCosts[_reportingWindow];
        if (_gasToReport != 0) {
            return _gasToReport;
        }

        IReportingWindow _previousReportingWindow = _reportingWindow.getPreviousReportingWindow();
        uint256 _estimatedReportsPerMarket = _previousReportingWindow.getAvgReportsPerMarket();
        uint256 _avgGasCost = _previousReportingWindow.getAvgReportingGasCost();
        _gasToReport = Reporting.gasToReport();
        // we double it to try and ensure we have more than enough rather than not enough
        targetReporterGasCosts[_reportingWindow] = _gasToReport * _estimatedReportsPerMarket * _avgGasCost * 2;
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

    function getMarketCreationCost(IReportingWindow _reportingWindow) constant public returns (uint256) {
        return getValidityBond(_reportingWindow) + getTargetReporterGasCosts(_reportingWindow);
    }
}
