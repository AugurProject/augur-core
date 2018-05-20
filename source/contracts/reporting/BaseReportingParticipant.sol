pragma solidity 0.4.20;

import 'reporting/IReportingParticipant.sol';
import 'reporting/IMarket.sol';
import 'reporting/IFeeWindow.sol';
import 'reporting/IReputationToken.sol';
import 'Controlled.sol';


contract BaseReportingParticipant is Controlled, IReportingParticipant {
    bool internal invalid;
    IMarket internal market;
    uint256 internal size;
    bytes32 internal payoutDistributionHash;
    IFeeWindow internal feeWindow;
    uint256[] internal payoutNumerators;
    IReputationToken internal reputationToken;
    ICash internal cash;

    function migrate() public onlyInGoodTimes returns (bool) {
        require(IMarket(msg.sender) == market);
        uint256 _balance = feeWindow.getFeeToken().balanceOf(this);
        feeWindow = market.getFeeWindow();
        feeWindow.mintFeeTokens(_balance);
        return true;
    }

    function liquidateLosing() public onlyInGoodTimes returns (bool) {
        require(IMarket(msg.sender) == market);
        require(market.getWinningPayoutDistributionHash() != getPayoutDistributionHash() && market.getWinningPayoutDistributionHash() != bytes32(0));
        IReputationToken _reputationToken = market.getReputationToken();
        require(_reputationToken.transfer(market, _reputationToken.balanceOf(this)));
        return true;
    }

    function fork() internal onlyInGoodTimes returns (bool) {
        require(market == market.getUniverse().getForkingMarket());
        IUniverse _newUniverse = market.getUniverse().createChildUniverse(payoutNumerators, invalid);
        IReputationToken _newReputationToken = _newUniverse.getReputationToken();
        redeemForAllFeeWindows();
        uint256 _balance = reputationToken.balanceOf(this);
        reputationToken.migrateOut(_newReputationToken, _balance);
        _newReputationToken.mintForReportingParticipant(_balance);
        reputationToken = _newReputationToken;
        controller.getAugur().logReportingParticipantDisavowed(market.getUniverse(), market);
        market = IMarket(0);
        return true;
    }

    function redeemForAllFeeWindows() internal returns (bool) {
        IFeeWindow _curFeeWindow = feeWindow;
        IUniverse _universe = feeWindow.getUniverse();
        while (_curFeeWindow.getFeeToken().balanceOf(this) > 0) {
            _curFeeWindow.redeemForReportingParticipant();
            _curFeeWindow = _universe.getOrCreateFeeWindowBefore(_curFeeWindow);
        }
        return true;
    }

    function isInvalid() public view returns (bool) {
        return invalid;
    }

    function getSize() public view returns (uint256) {
        return size;
    }

    function getPayoutDistributionHash() public view returns (bytes32) {
        return payoutDistributionHash;
    }

    function getMarket() public view returns (IMarket) {
        return market;
    }

    function isDisavowed() public view returns (bool) {
        return market == IMarket(0) || !market.isContainerForReportingParticipant(this);
    }

    function getPayoutNumerator(uint256 _outcome) public view returns (uint256) {
        return payoutNumerators[_outcome];
    }
}
