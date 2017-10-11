pragma solidity 0.4.17;


import 'reporting/IReportingToken.sol';
import 'libraries/DelegationTarget.sol';
import 'libraries/Typed.sol';
import 'libraries/Initializable.sol';
import 'libraries/token/VariableSupplyToken.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReputationToken.sol';
import 'reporting/IReportingToken.sol';
import 'reporting/IDisputeBond.sol';
import 'reporting/IReportingWindow.sol';
import 'reporting/IMarket.sol';
import 'libraries/math/SafeMathUint256.sol';
import 'extensions/MarketFeeCalculator.sol';


contract ReportingToken is DelegationTarget, Typed, Initializable, VariableSupplyToken, IReportingToken {
    using SafeMathUint256 for uint256;

    IMarket public market;
    uint256[] public payoutNumerators;

    function initialize(IMarket _market, uint256[] _payoutNumerators) public beforeInitialized returns (bool) {
        endInitialization();
        require(_market.getNumberOfOutcomes() == _payoutNumerators.length);
        uint256 _sum = 0;
        for (uint8 i = 0; i < _payoutNumerators.length; i++) {
            _sum = _sum.add(_payoutNumerators[i]);
        }
        require(_sum == _market.getNumTicks());
        market = _market;
        payoutNumerators = _payoutNumerators;
        return true;
    }

    function buy(uint256 _attotokens) public afterInitialized returns (bool) {
        IMarket.ReportingState _state = market.getReportingState();
        // If this is the first report and there was no designated reporter we ask the market to compensate them and get back the amount of extra REP to automatically stake against this outcome
        _attotokens = _attotokens.add(market.round1ReporterCompensationCheck(msg.sender));
        require(_attotokens > 0);
        if (_state == IMarket.ReportingState.AWAITING_NO_REPORT_MIGRATION) {
            market.migrateDueToNoReports();
        } else if (_state == IMarket.ReportingState.DESIGNATED_REPORTING) {
            require(msg.sender == market.getDesignatedReporter());
            uint256 _designatedReportCost = MarketFeeCalculator(controller.lookup("MarketFeeCalculator")).getDesignatedReportStake(market.getUniverse());
            require(_attotokens == _designatedReportCost);
        } else {
            require(_state == IMarket.ReportingState.ROUND1_REPORTING || _state == IMarket.ReportingState.ROUND2_REPORTING);
        }
        buyTokens(msg.sender, _attotokens);
        if (_state == IMarket.ReportingState.DESIGNATED_REPORTING) {
            market.designatedReport();
        }
        return true;
    }

    function trustedBuy(address _reporter, uint256 _attotokens) public afterInitialized returns (bool) {
        require(IMarket(msg.sender) == market);
        require(_attotokens > 0);
        IMarket.ReportingState _state = market.getReportingState();
        require(_state == IMarket.ReportingState.ROUND1_REPORTING || _state == IMarket.ReportingState.ROUND2_REPORTING);
        buyTokens(_reporter, _attotokens);
    }

    function buyTokens(address _reporter, uint256 _attotokens) private afterInitialized returns (bool) {
        require(market.isContainerForReportingToken(this));
        getReputationToken().trustedTransfer(_reporter, this, _attotokens);
        mint(_reporter, _attotokens);
        bytes32 _payoutDistributionHash = getPayoutDistributionHash();
        market.updateTentativeWinningPayoutDistributionHash(_payoutDistributionHash);
        getReportingWindow().noteReportingGasPrice(market);
    } 

    function redeemDisavowedTokens(address _reporter) public afterInitialized returns (bool) {
        require(!market.isContainerForReportingToken(this));
        uint256 _reputationSupply = getReputationToken().balanceOf(this);
        uint256 _attotokens = balances[_reporter];
        uint256 _reporterReputationShare = _reputationSupply * _attotokens / supply;
        burn(_reporter, _attotokens);
        getReputationToken().transfer(_reporter, _reporterReputationShare);
        return true;
    }

    // NOTE: UI should warn users about calling this before first calling `migrateLosingTokens` on all losing tokens with non-dust contents
    function redeemForkedTokens() public afterInitialized returns (bool) {
        require(market.isContainerForReportingToken(this));
        require(getUniverse().getForkingMarket() == market);
        IReputationToken _sourceReputationToken = getReputationToken();
        uint256 _reputationSupply = _sourceReputationToken.balanceOf(this);
        uint256 _attotokens = balances[msg.sender];
        uint256 _reporterReputationShare = _reputationSupply * _attotokens / supply;
        burn(msg.sender, _attotokens);
        IReputationToken _destinationReputationToken = getUniverse().getOrCreateChildUniverse(getPayoutDistributionHash()).getReputationToken();
        _sourceReputationToken.migrateOut(_destinationReputationToken, this, _attotokens);
        _destinationReputationToken.transfer(msg.sender, _reporterReputationShare);
        return true;
    }

    // NOTE: UI should warn users about calling this before first calling `migrateLosingTokens` on all losing tokens with non-dust contents
    // NOTE: we aren't using the convertToAndFromCash modifier here becuase this isn't a whitelisted contract. We expect the reporting window to handle disbursment of ETH
    function redeemWinningTokens() public afterInitialized returns (bool) {
        require(market.getReportingState() == IMarket.ReportingState.FINALIZED);
        require(market.isContainerForReportingToken(this));
        require(getUniverse().getForkingMarket() != market);
        require(market.getFinalWinningReportingToken() == this);
        IReportingWindow _reportingWindow = market.getReportingWindow();
        require(_reportingWindow.allMarketsFinalized());
        IReputationToken _reputationToken = getReputationToken();
        uint256 _reputationSupply = _reputationToken.balanceOf(this);
        uint256 _attotokens = balances[msg.sender];
        uint256 _reporterReputationShare = _reputationSupply * _attotokens / supply;
        burn(msg.sender, _attotokens);
        if (_reporterReputationShare != 0) {
            _reputationToken.transfer(msg.sender, _reporterReputationShare);
        }
        _reportingWindow.collectReportingFees(msg.sender, _attotokens);
        return true;
    }

    function migrateLosingTokens() public afterInitialized returns (bool) {
        require(market.getReportingState() == IMarket.ReportingState.FINALIZED);
        require(market.isContainerForReportingToken(this));
        require(getUniverse().getForkingMarket() != market);
        require(market.getFinalWinningReportingToken() != this);
        migrateLosingTokenRepToDisputeBond(market.getDesignatedReporterDisputeBondToken());
        migrateLosingTokenRepToDisputeBond(market.getRound1ReportersDisputeBondToken());
        migrateLosingTokenRepToWinningToken();
        return true;
    }

    function migrateLosingTokenRepToDisputeBond(IDisputeBond _disputeBondToken) private returns (bool) {
        if (_disputeBondToken == address(0)) {
            return true;
        }
        if (_disputeBondToken.getDisputedPayoutDistributionHash() == market.getFinalPayoutDistributionHash()) {
            return true;
        }
        IReputationToken _reputationToken = getReputationToken();
        uint256 _amountNeeded = _disputeBondToken.getBondRemainingToBePaidOut() - _reputationToken.balanceOf(_disputeBondToken);
        uint256 _amountToTransfer = _amountNeeded.min(_reputationToken.balanceOf(this));
        if (_amountToTransfer == 0) {
            return true;
        }
        _reputationToken.transfer(_disputeBondToken, _amountToTransfer);
        return true;
    }

    function migrateLosingTokenRepToWinningToken() private returns (bool) {
        IReputationToken _reputationToken = getReputationToken();
        uint256 _balance = _reputationToken.balanceOf(this);
        if (_balance == 0) {
            return true;
        }
        _reputationToken.transfer(market.getFinalWinningReportingToken(), _balance);
        return true;
    }

    function getTypeName() public view returns (bytes32) {
        return "ReportingToken";
    }

    function getUniverse() public view returns (IUniverse) {
        return market.getUniverse();
    }

    function getReputationToken() public view returns (IReputationToken) {
        return market.getReportingWindow().getReputationToken();
    }

    function getReportingWindow() public view returns (IReportingWindow) {
        return market.getReportingWindow();
    }

    function getMarket() public view returns (IMarket) {
        return market;
    }

    function getPayoutDistributionHash() public view returns (bytes32) {
        return market.derivePayoutDistributionHash(payoutNumerators);
    }

    function getPayoutNumerator(uint8 index) public view returns (uint256) {
        require(index < market.getNumberOfOutcomes());
        return payoutNumerators[index];
    }

    function isValid() public view returns (bool) {
        for (uint8 i = 1; i < payoutNumerators.length; i++) {
            if (payoutNumerators[0] != payoutNumerators[i]) {
                return true;
            }
        }
        return false;
    }
}
