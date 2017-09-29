pragma solidity ^0.4.13;

import 'reporting/IReputationToken.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReportingWindow.sol';
import 'libraries/math/SafeMathUint256.sol';


contract MarketFeeCalculator {
    using SafeMathUint256 for uint256;

    mapping (address => uint256) private shareSettlementPerEthFee;
    mapping (address => uint256) private validityBondInAttoeth;

    uint256 private constant DEFAULT_VALIDITY_BOND = 1 ether;
    uint256 private constant FXP_TARGET_INDETERMINATE_MARKETS = 10 ** 16; // 1% of markets

    function getValidityBond(IReportingWindow _reportingWindow) public returns (uint256) {
        uint256 _currentValidityBondInAttoeth = validityBondInAttoeth[_reportingWindow];
        if (_currentValidityBondInAttoeth != 0) {
            return _currentValidityBondInAttoeth;
        }
        uint256 _previousTimestamp = _reportingWindow.getStartTime() - 1;
        IUniverse _universe = _reportingWindow.getUniverse();
        IReportingWindow _previousReportingWindow = _universe.getReportingWindowByTimestamp(_previousTimestamp);
        uint256 _totalMarketsInPreviousWindow = _reportingWindow.getNumMarkets();
        uint256 _indeterminateMarketsInPreviousWindow = _reportingWindow.getNumIndeterminateMarkets();
        uint256 _previousValidityBondInAttoeth = validityBondInAttoeth[_previousReportingWindow];

        _currentValidityBondInAttoeth = calculateValidityBond(_indeterminateMarketsInPreviousWindow, _totalMarketsInPreviousWindow, FXP_TARGET_INDETERMINATE_MARKETS, _previousValidityBondInAttoeth);
        validityBondInAttoeth[_reportingWindow] = _currentValidityBondInAttoeth;
        return _currentValidityBondInAttoeth;
    }

    function calculateValidityBond(uint256 _indeterminateMarkets, uint256 _totalMarkets, uint256 _fxpTargetIndeterminateMarkets, uint256 _previousValidityBondInAttoeth) constant public returns (uint256) {
        if (_totalMarkets == 0) {
            return DEFAULT_VALIDITY_BOND;
        }
        if (_previousValidityBondInAttoeth == 0) {
            _previousValidityBondInAttoeth = DEFAULT_VALIDITY_BOND;
        }
        
        uint256 _fxpBase = uint256(1 ether);
        uint256 _fxpPercentIndeterminate = _indeterminateMarkets.fxpDiv(_totalMarkets, _fxpBase);
        uint256 _fxpMultiple = _fxpBase;

        if (_fxpPercentIndeterminate <= _fxpTargetIndeterminateMarkets) {
            _fxpMultiple = _fxpPercentIndeterminate.fxpDiv(_fxpTargetIndeterminateMarkets.mul(2), _fxpBase).add(_fxpBase.div(2));
        } else {
            _fxpMultiple = _fxpBase.fxpDiv(_fxpBase.sub(_fxpTargetIndeterminateMarkets), _fxpBase).fxpMul(_fxpPercentIndeterminate.sub(_fxpTargetIndeterminateMarkets), _fxpBase).add(_fxpBase);
        }

        return _previousValidityBondInAttoeth.fxpMul(_fxpMultiple, _fxpBase);
    }

    function getTargetReporterGasCosts() constant public returns (uint256) {
        // TODO: get number of registration tokens issued last period
        // TODO: get target reporter count + wiggle room
        // TODO: calculate estimated reporters per market
        uint256 _estimatedReportsPerMarket = 10;
        // TODO: figure out what the number actually is
        uint256 _gasToReport = 100000;
        // we double it to ensure we have more than enough rather than not enough
        uint256 _estimatedReportingGas = _gasToReport * _estimatedReportsPerMarket * 2;
        // TODO: multiply this by average gas costs of reporters historically
        return _estimatedReportingGas;
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
        uint256 _previousTimestamp = _reportingWindow.getStartTime() - 1;
        IReportingWindow _previousReportingWindow = _universe.getReportingWindowByTimestamp(_previousTimestamp);
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
        // TODO: get these from an auto-generated market
        uint256 _attorepPerEth = 11 * 10 ** 18;
        uint256 _repMarketCapInAttoeth = _universe.getReputationToken().totalSupply() * _attorepPerEth;
        return _repMarketCapInAttoeth;
    }

    function getTargetRepMarketCapInAttoeth(IReportingWindow _reportingWindow) constant public returns (uint256) {
        uint256 _outstandingSharesInAttoeth = getOutstandingSharesInAttoeth(_reportingWindow);
        uint256 _targetRepMarketCapInAttoeth = _outstandingSharesInAttoeth * 5;
        return _targetRepMarketCapInAttoeth;
    }

    function getOutstandingSharesInAttoeth(IReportingWindow) constant public returns (uint256) {
        // TODO: start tracking the real number and store it somewhere
        // NOTE: make sure we are getting the share value in attoeth, since complete set fees are not normalized across markets
        // NOTE: eventually we will need to support shares in multiple denominations
        uint256 _outstandingSharesInAttoeth = 100 * 10 ** 18;
        return _outstandingSharesInAttoeth;
    }

    function getMarketCreationCost(IReportingWindow _reportingWindow) constant public returns (uint256) {
        return getValidityBond(_reportingWindow) + getTargetReporterGasCosts();
    }
}
