pragma solidity 0.4.18;

import 'libraries/Initializable.sol';
import 'libraries/DelegationTarget.sol';
import 'reporting/IInitialReporter.sol';
import 'reporting/IMarket.sol';
import 'reporting/BaseReportingParticipant.sol';


contract InitialReporter is DelegationTarget, BaseReportingParticipant, Initializable, IInitialReporter {
    address private designatedReporter;
    address private actualReporter;
    uint256 private reportTimestamp;

    function initialize(IMarket _market, address _designatedReporter) public onlyInGoodTimes beforeInitialized returns (bool) {
        endInitialization();
        market = _market;
        designatedReporter = _designatedReporter;
        return true;
    }

    function depositGasBond() public payable returns (bool) {
        return true;
    }

    function redeem(address _redeemer) public returns (bool) {
        require(market.getWinningPayoutDistributionHash() == payoutDistributionHash);
        feeWindow.redeem(this);
        IReputationToken _reputationToken = market.getReputationToken();
        _reputationToken.transfer(_redeemer, _reputationToken.balanceOf(this));
        require(actualReporter.call.value(this.balance)());
        return true;
    }

    function report(address _reporter, bytes32 _payoutDistributionHash, uint256[] _payoutNumerators, bool _invalid) public onlyInGoodTimes returns (bool) {
        require(IMarket(msg.sender) == market);
        actualReporter = _reporter;
        payoutDistributionHash = _payoutDistributionHash;
        reportTimestamp = controller.getTimestamp();
        invalid = _invalid;
        payoutNumerators = _payoutNumerators;
        size = market.getReputationToken().balanceOf(this);
        feeWindow = market.getFeeWindow();
        feeWindow.noteInitialReportingGasPrice();
        feeWindow.buy(size);
        return true;
    }

    function fork() public onlyInGoodTimes returns (bool) {
        IUniverse _newUniverse = market.getUniverse().createChildUniverse(payoutDistributionHash);
        IReputationToken _newReputationToken = _newUniverse.getReputationToken();
        IReputationToken _reputationToken = market.getReputationToken();
        // TODO feeWindow.redeem(this);
        _reputationToken.migrateOut(_newReputationToken, _reputationToken.balanceOf(this));
        _newReputationToken.transfer(actualReporter, _newReputationToken.balanceOf(this));
        return true;
    }

    function resetReportTimestamp() public onlyInGoodTimes returns (bool) {
        require(IMarket(msg.sender) == market);
        if (reportTimestamp == 0) {
            return;
        }
        reportTimestamp = controller.getTimestamp();
        return true;
    }

    function getStake() public view returns (uint256) {
        return size;
    }

    function getDesignatedReporter() public view returns (address) {
        return designatedReporter;
    }

    function getReportTimestamp() public view returns (uint256) {
        return reportTimestamp;
    }

    function designatedReporterShowed() public view returns (bool) {
        return actualReporter == designatedReporter;
    }
    
    function designatedReporterWasCorrect() public view returns (bool) {
        return payoutDistributionHash == market.getWinningPayoutDistributionHash();
    }
}
