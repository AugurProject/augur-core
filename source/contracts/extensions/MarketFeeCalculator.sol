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
    uint256 private constant TARGET_INDETERMINATE_MARKETS_DIVISOR = 100; // 1% of markets
    uint256 private constant TARGET_REP_MARKET_CAP_MULTIPLIER = 5;

    function getValidityBond(IReportingWindow _reportingWindow) public returns (uint256) {
        uint256 _currentValidityBondInAttoeth = validityBondInAttoeth[_reportingWindow];
        if (_currentValidityBondInAttoeth != 0) {
            return _currentValidityBondInAttoeth;
        }
        IReportingWindow _previousReportingWindow = _reportingWindow.getPreviousReportingWindow();
        uint256 _totalMarketsInPreviousWindow = _reportingWindow.getNumMarkets();
        uint256 _indeterminateMarketsInPreviousWindow = _reportingWindow.getNumIndeterminateMarkets();
        uint256 _previousValidityBondInAttoeth = validityBondInAttoeth[_previousReportingWindow];

        _currentValidityBondInAttoeth = calculateValidityBond(_indeterminateMarketsInPreviousWindow, _totalMarketsInPreviousWindow, TARGET_INDETERMINATE_MARKETS_DIVISOR, _previousValidityBondInAttoeth);
        validityBondInAttoeth[_reportingWindow] = _currentValidityBondInAttoeth;
        return _currentValidityBondInAttoeth;
    }

    function calculateValidityBond(uint256 _indeterminateMarkets, uint256 _totalMarkets, uint256 _targetIndeterminateMarketsDivisor, uint256 _previousValidityBondInAttoeth) constant public returns (uint256) {
        if (_totalMarkets == 0) {
            return DEFAULT_VALIDITY_BOND;
        }
        if (_previousValidityBondInAttoeth == 0) {
            _previousValidityBondInAttoeth = DEFAULT_VALIDITY_BOND;
        }
        
        uint256 _targetIndeterminateMarkets = _totalMarkets.div(_targetIndeterminateMarketsDivisor);

        if (_indeterminateMarkets <= _targetIndeterminateMarkets) {
            return _indeterminateMarkets
                .mul(_previousValidityBondInAttoeth)
                .mul(_targetIndeterminateMarketsDivisor)
                .div(_totalMarkets)
                .div(2)
            .add(_previousValidityBondInAttoeth.div(2));
        } else {
            return _targetIndeterminateMarketsDivisor
                .mul(_previousValidityBondInAttoeth.mul(_indeterminateMarkets)
                .div(_totalMarkets)
                .sub(_previousValidityBondInAttoeth.div(_targetIndeterminateMarketsDivisor)))
                .div(_targetIndeterminateMarketsDivisor - 1)
            .add(_previousValidityBondInAttoeth);
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
        // TODO: get this from an auto-generated market or some other special contract
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
