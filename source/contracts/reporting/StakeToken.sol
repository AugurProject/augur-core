pragma solidity 0.4.17;


import 'reporting/IStakeToken.sol';
import 'libraries/DelegationTarget.sol';
import 'libraries/ITyped.sol';
import 'libraries/Initializable.sol';
import 'libraries/token/VariableSupplyToken.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReputationToken.sol';
import 'reporting/IStakeToken.sol';
import 'reporting/IDisputeBond.sol';
import 'reporting/IReportingWindow.sol';
import 'reporting/IMarket.sol';
import 'libraries/math/SafeMathUint256.sol';
import 'Augur.sol';
import 'libraries/Extractable.sol';


contract StakeToken is DelegationTarget, Extractable, ITyped, Initializable, VariableSupplyToken, IStakeToken {
    using SafeMathUint256 for uint256;

    IMarket public market;
    uint256[] public payoutNumerators;
    bool private invalid;

    function initialize(IMarket _market, uint256[] _payoutNumerators, bool _invalid) public onlyInGoodTimes beforeInitialized returns (bool) {
        endInitialization();
        require(_market.getNumberOfOutcomes() == _payoutNumerators.length);
        uint256 _sum = 0;
        for (uint8 i = 0; i < _payoutNumerators.length; i++) {
            _sum = _sum.add(_payoutNumerators[i]);
        }
        require(_sum == _market.getNumTicks());
        require(!invalid || isInvalidOutcome());
        market = _market;
        payoutNumerators = _payoutNumerators;
        invalid = _invalid;
        return true;
    }

    function buy(uint256 _attotokens) public onlyInGoodTimes afterInitialized returns (bool) {
        IMarket.ReportingState _state = market.getReportingState();
        // If this is the first report and there was no designated reporter we ask the market to compensate them and get back the amount of extra REP to automatically stake against this outcome
        _attotokens = _attotokens.add(market.firstReporterCompensationCheck(msg.sender));
        require(_attotokens > 0);
        if (_state == IMarket.ReportingState.AWAITING_NO_REPORT_MIGRATION) {
            market.migrateDueToNoReports();
        } else if (_state == IMarket.ReportingState.DESIGNATED_REPORTING) {
            require(msg.sender == market.getDesignatedReporter());
            uint256 _designatedReportCost = market.getUniverse().getDesignatedReportStake();
            require(_attotokens == _designatedReportCost);
        } else {
            require(_state == IMarket.ReportingState.FIRST_REPORTING || _state == IMarket.ReportingState.LAST_REPORTING);
        }
        buyTokens(msg.sender, _attotokens);
        if (_state == IMarket.ReportingState.DESIGNATED_REPORTING) {
            market.designatedReport();
            controller.getAugur().logDesignatedReportSubmitted(market.getUniverse(), msg.sender, market, this, _attotokens, payoutNumerators);
        } else {
            controller.getAugur().logReportSubmitted(market.getUniverse(), msg.sender, market, this, _attotokens, payoutNumerators);
        }
        return true;
    }

    function trustedBuy(address _reporter, uint256 _attotokens) public onlyInGoodTimes afterInitialized returns (bool) {
        require(IMarket(msg.sender) == market);
        require(_attotokens > 0);
        IMarket.ReportingState _state = market.getReportingState();
        require(_state == IMarket.ReportingState.FIRST_REPORTING || _state == IMarket.ReportingState.LAST_REPORTING);
        buyTokens(_reporter, _attotokens);
        return true;
    }

    function buyTokens(address _reporter, uint256 _attotokens) private onlyInGoodTimes afterInitialized returns (bool) {
        getReputationToken().trustedStakeTokenTransfer(_reporter, this, _attotokens);
        mint(_reporter, _attotokens);
        bytes32 _payoutDistributionHash = getPayoutDistributionHash();
        market.increaseTotalStake(_attotokens);
        market.updateTentativeWinningPayoutDistributionHash(_payoutDistributionHash);
        getReportingWindow().noteReportingGasPrice(market);
        return true;
    }

    function redeemDisavowedTokens(address _reporter) public onlyInGoodTimes afterInitialized returns (bool) {
        require(!market.isContainerForStakeToken(this));
        uint256 _reputationSupply = getReputationToken().balanceOf(this);
        uint256 _attotokens = balances[_reporter];
        uint256 _reporterReputationShare = _reputationSupply * _attotokens / supply;
        burn(_reporter, _attotokens);
        getReputationToken().transfer(_reporter, _reporterReputationShare);
        return true;
    }

    // NOTE: UI should warn users about calling this before first calling `migrateLosingTokens` on all losing tokens with non-dust contents
    function redeemForkedTokens() public onlyInGoodTimes afterInitialized returns (bool) {
        require(market.isContainerForStakeToken(this));
        require(getUniverse().getForkingMarket() == market);
        uint256 _attotokens = balances[msg.sender];
        burn(msg.sender, _attotokens);
        IReputationToken _destinationReputationToken = getUniverse().getOrCreateChildUniverse(getPayoutDistributionHash()).getReputationToken();
        getReputationToken().migrateOutStakeToken(_destinationReputationToken, this, _attotokens);
        _destinationReputationToken.transfer(msg.sender, _destinationReputationToken.balanceOf(this));
        return true;
    }

    // NOTE: UI should warn users about calling this before first calling `migrateLosingTokens` on all losing tokens with non-dust contents
    // NOTE: we aren't using the convertToAndFromCash modifier here becuase this isn't a whitelisted contract. We expect the reporting window to handle disbursment of ETH
    function redeemWinningTokens(bool forgoFees) public onlyInGoodTimes afterInitialized returns (bool) {
        require(market.getFinalWinningStakeToken() == this);
        require(market.isContainerForStakeToken(this));
        require(getUniverse().getForkingMarket() != market);
        IReputationToken _reputationToken = getReputationToken();
        uint256 _reputationSupply = _reputationToken.balanceOf(this);
        uint256 _attotokens = balances[msg.sender];
        uint256 _reporterReputationShare = _reputationSupply * _attotokens / supply;
        burn(msg.sender, _attotokens);
        if (_reporterReputationShare != 0) {
            _reputationToken.transfer(msg.sender, _reporterReputationShare);
        }
        uint256 _feesReceived = market.getReportingWindow().collectStakeTokenReportingFees(msg.sender, _attotokens, forgoFees);
        controller.getAugur().logWinningTokensRedeemed(market.getUniverse(), msg.sender, market, this, _attotokens, _feesReceived, payoutNumerators);
        return true;
    }

    function migrateLosingTokens() public onlyInGoodTimes afterInitialized returns (bool) {
        require(market.getReportingState() == IMarket.ReportingState.FINALIZED);
        require(market.isContainerForStakeToken(this));
        require(getUniverse().getForkingMarket() != market);
        require(market.getFinalWinningStakeToken() != this);
        migrateLosingTokenRepToDisputeBond(market.getDesignatedReporterDisputeBond());
        migrateLosingTokenRepToDisputeBond(market.getFirstReportersDisputeBond());
        migrateLosingTokenRepToWinningToken();
        return true;
    }

    function migrateLosingTokenRepToDisputeBond(IDisputeBond _disputeBond) private onlyInGoodTimes returns (bool) {
        if (_disputeBond == address(0)) {
            return true;
        }
        if (_disputeBond.getDisputedPayoutDistributionHash() == market.getFinalPayoutDistributionHash()) {
            return true;
        }
        IReputationToken _reputationToken = getReputationToken();
        uint256 _amountNeeded = _disputeBond.getBondRemainingToBePaidOut() - _reputationToken.balanceOf(_disputeBond);
        uint256 _amountToTransfer = _amountNeeded.min(_reputationToken.balanceOf(this));
        if (_amountToTransfer == 0) {
            return true;
        }
        _reputationToken.transfer(_disputeBond, _amountToTransfer);
        return true;
    }

    function migrateLosingTokenRepToWinningToken() private onlyInGoodTimes returns (bool) {
        IReputationToken _reputationToken = getReputationToken();
        uint256 _balance = _reputationToken.balanceOf(this);
        if (_balance == 0) {
            return true;
        }
        _reputationToken.transfer(market.getFinalWinningStakeToken(), _balance);
        return true;
    }

    function withdrawInEmergency() public onlyInBadTimes returns (bool) {
        IReputationToken _reputationToken = getReputationToken();
        uint256 _reputationSupply = _reputationToken.balanceOf(this);
        uint256 _attotokens = balances[msg.sender];
        uint256 _reporterReputationShare = _reputationSupply * _attotokens / supply;
        burn(msg.sender, _attotokens);
        if (_reporterReputationShare != 0) {
            _reputationToken.transfer(msg.sender, _reporterReputationShare);
        }
        return true;
    }

    function getTypeName() public view returns (bytes32) {
        return "StakeToken";
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
        return market.derivePayoutDistributionHash(payoutNumerators, invalid);
    }

    function getPayoutNumerator(uint8 index) public view returns (uint256) {
        require(index < market.getNumberOfOutcomes());
        return payoutNumerators[index];
    }

    function isValid() public view returns (bool) {
        return !invalid;
    }

    function isInvalidOutcome() private view returns (bool) {
        for (uint8 i = 1; i < payoutNumerators.length; i++) {
            if (payoutNumerators[0] != payoutNumerators[i]) {
                return false;
            }
        }
        return true;
    }

    function onTokenTransfer(address _from, address _to, uint256 _value) internal returns (bool) {
        controller.getAugur().logStakeTokensTransferred(market.getUniverse(), _from, _to, _value);
        return true;
    }

    function onMint(address _target, uint256 _amount) internal returns (bool) {
        controller.getAugur().logStakeTokenMinted(market.getUniverse(), _target, _amount);
        return true;
    }

    function onBurn(address _target, uint256 _amount) internal returns (bool) {
        controller.getAugur().logStakeTokenBurned(market.getUniverse(), _target, _amount);
        return true;
    }

    // Disallow REP extraction
    function getProtectedTokens() internal returns (address[] memory) {
        address[] memory _protectedTokens = new address[](1);
        _protectedTokens[0] = getReputationToken();
        return _protectedTokens;
    }
}
