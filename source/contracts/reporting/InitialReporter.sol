pragma solidity 0.4.24;

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

    function initialize(IMarket _market, address _designatedReporter) public beforeInitialized returns (bool) {
        endInitialization();
        market = _market;
        reputationToken = market.getUniverse().getReputationToken();
        designatedReporter = _designatedReporter;
        return true;
    }

    function redeem(address) public returns (bool) {
        bool _isDisavowed = isDisavowed();
        if (!_isDisavowed && !market.isFinalized()) {
            market.finalize();
        }
        uint256 _repBalance = reputationToken.balanceOf(this);
        require(reputationToken.transfer(owner, _repBalance));
        if (!_isDisavowed) {
            controller.getAugur().logInitialReporterRedeemed(market.getUniverse(), owner, market, size, _repBalance, payoutNumerators);
        }
        return true;
    }

    function report(address _reporter, bytes32 _payoutDistributionHash, uint256[] _payoutNumerators, uint256 _initialReportStake) public returns (bool) {
        require(IMarket(msg.sender) == market);
        require(reportTimestamp == 0);
        uint256 _timestamp = controller.getTimestamp();
        bool _isDesignatedReporter = _reporter == getDesignatedReporter();
        bool _designatedReportingExpired = _timestamp > market.getDesignatedReportingEndTime();
        require(_designatedReportingExpired || _isDesignatedReporter);
        actualReporter = _reporter;
        owner = _reporter;
        payoutDistributionHash = _payoutDistributionHash;
        reportTimestamp = _timestamp;
        payoutNumerators = _payoutNumerators;
        size = _initialReportStake;
        return true;
    }

    function returnRepFromDisavow() public returns (bool) {
        require(IMarket(msg.sender) == market);
        require(reputationToken.transfer(owner, reputationToken.balanceOf(this)));
        reportTimestamp = 0;
        return true;
    }

    function migrateToNewUniverse(address _designatedReporter) public returns (bool) {
        require(IMarket(msg.sender) == market);
        designatedReporter = _designatedReporter;
        reputationToken = market.getUniverse().getReputationToken();
        return true;
    }

    function forkAndRedeem() public returns (bool) {
        if (!isDisavowed()) {
            controller.getAugur().logInitialReporterRedeemed(market.getUniverse(), owner, market, size, reputationToken.balanceOf(this), payoutNumerators);
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
