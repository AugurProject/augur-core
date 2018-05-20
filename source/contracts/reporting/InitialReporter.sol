pragma solidity 0.4.20;

import 'libraries/Initializable.sol';
import 'libraries/DelegationTarget.sol';
import 'reporting/IInitialReporter.sol';
import 'reporting/IMarket.sol';
import 'reporting/BaseReportingParticipant.sol';
import 'libraries/Ownable.sol';


contract InitialReporter is DelegationTarget, Ownable, BaseReportingParticipant, Initializable, IInitialReporter {
    address private designatedReporter;
    address private actualReporter;
    uint256 private reportTimestamp;

    function initialize(IMarket _market, address _designatedReporter) public onlyInGoodTimes beforeInitialized returns (bool) {
        endInitialization();
        market = _market;
        reputationToken = market.getUniverse().getReputationToken();
        cash = market.getDenominationToken();
        designatedReporter = _designatedReporter;
        return true;
    }

    function redeem(address) public returns (bool) {
        bool _isDisavowed = isDisavowed();
        if (!_isDisavowed && !market.isFinalized()) {
            market.finalize();
        }
        redeemForAllFeeWindows();
        uint256 _repBalance = reputationToken.balanceOf(this);
        require(reputationToken.transfer(owner, _repBalance));
        uint256 _cashBalance = cash.balanceOf(this);
        if (_cashBalance > 0) {
            cash.withdrawEtherTo(owner, _cashBalance);
        }
        if (!_isDisavowed) {
            controller.getAugur().logInitialReporterRedeemed(market.getUniverse(), owner, market, size, _repBalance, _cashBalance, payoutNumerators);
        }
        return true;
    }

    function report(address _reporter, bytes32 _payoutDistributionHash, uint256[] _payoutNumerators, bool _invalid) public onlyInGoodTimes returns (bool) {
        require(IMarket(msg.sender) == market);
        actualReporter = _reporter;
        owner = _reporter;
        payoutDistributionHash = _payoutDistributionHash;
        reportTimestamp = controller.getTimestamp();
        invalid = _invalid;
        payoutNumerators = _payoutNumerators;
        size = reputationToken.balanceOf(this);
        feeWindow = market.getFeeWindow();
        feeWindow.noteInitialReportingGasPrice();
        feeWindow.mintFeeTokens(size);
        return true;
    }

    function withdrawInEmergency() public onlyInBadTimes returns (bool) {
        require(reputationToken.transfer(owner, reputationToken.balanceOf(this)));
        uint256 _cashBalance = cash.balanceOf(this);
        if (_cashBalance > 0) {
            cash.withdrawEtherTo(owner, _cashBalance);
        }
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

    function migrateREP() public returns (bool) {
        require(IMarket(msg.sender) == market);
        IUniverse _newUniverse = market.getUniverse();
        IReputationToken _newReputationToken = _newUniverse.getReputationToken();
        uint256 _balance = reputationToken.balanceOf(this);
        if (_balance > 0) {
            reputationToken.migrateOut(_newReputationToken, _balance);
        }
        reputationToken = _newReputationToken;
        return true;
    }

    function forkAndRedeem() public onlyInGoodTimes returns (bool) {
        if (!isDisavowed()) {
            controller.getAugur().logInitialReporterRedeemed(market.getUniverse(), owner, market, size, reputationToken.balanceOf(this), cash.balanceOf(this), payoutNumerators);
        }
        fork();
        redeem(msg.sender);
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

    function getFeeWindow() public view returns (IFeeWindow) {
        return feeWindow;
    }

    function getReputationToken() public view returns (IReputationToken) {
        return reputationToken;
    }

    function designatedReporterWasCorrect() public view returns (bool) {
        return payoutDistributionHash == market.getWinningPayoutDistributionHash();
    }

    function onTransferOwnership(address _owner, address _newOwner) internal returns (bool) {
        controller.getAugur().logInitialReporterTransferred(market.getUniverse(), market, _owner, _newOwner);
        return true;
    }
}
