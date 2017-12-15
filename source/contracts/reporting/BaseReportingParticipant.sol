pragma solidity 0.4.18;

import 'reporting/IReportingParticipant.sol';
import 'reporting/IMarket.sol';
import 'reporting/IFeeWindow.sol';
import 'Controlled.sol';


contract BaseReportingParticipant is Controlled, IReportingParticipant {
    bool internal invalid;
    IMarket internal market;
    uint256 internal size;
    bytes32 internal payoutDistributionHash;
    IFeeWindow internal feeWindow;
    uint256[] internal payoutNumerators;

    function migrate() public onlyInGoodTimes returns (bool) {
        require(IMarket(msg.sender) == market);
        uint256 _balance = feeWindow.balanceOf(this);
        feeWindow.redeem(this);
        feeWindow = market.getFeeWindow();
        feeWindow.buy(_balance);
    }

    function liquidateLosing() public onlyInGoodTimes returns (bool) {
        require(market.getWinningPayoutDistributionHash() != getPayoutDistributionHash() && market.getWinningPayoutDistributionHash() != bytes32(0));
        IReputationToken _reputationToken = market.getReputationToken();
        feeWindow.redeem(this);
        _reputationToken.transfer(market, _reputationToken.balanceOf(this));
        ICash _cash = ICash(controller.lookup("Cash"));
        _cash.depositEtherFor.value(this.balance)(market.getFeeWindow());
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

    function isDisavowed() public returns (bool) {
        return market == IMarket(0);
    }

    function getPayoutNumerator(uint8 _outcome) public view returns (uint256) {
        return payoutNumerators[_outcome];
    }
}
