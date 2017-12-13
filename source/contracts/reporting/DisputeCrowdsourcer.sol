pragma solidity 0.4.18;

import 'reporting/IDisputeCrowdsourcer.sol';
import 'libraries/token/VariableSupplyToken.sol';
import 'reporting/BaseReportingParticipant.sol';
import 'libraries/Initializable.sol';
import 'libraries/DelegationTarget.sol';


contract DisputeCrowdsourcer is DelegationTarget, VariableSupplyToken, BaseReportingParticipant, IDisputeCrowdsourcer, Initializable {

    function initialize(IMarket _market, uint256 _size, bytes32 _payoutDistributionHash, uint256[] _payoutNumerators, bool _invalid) public onlyInGoodTimes beforeInitialized returns (bool) {
        endInitialization();
        market = _market;
        feeWindow = market.getFeeWindow();
        size = _size;
        payoutNumerators = _payoutNumerators;
        payoutDistributionHash = _payoutDistributionHash;
        return true;
    }

    function redeem(address _redeemer) public onlyInGoodTimes returns (bool) {
        require(isDisavowed() || market.getWinningPayoutDistributionHash() == getPayoutDistributionHash());
        feeWindow.redeem(this);
        IReputationToken _reputationToken = market.getReputationToken();
        uint256 _reputationSupply = _reputationToken.balanceOf(this);
        uint256 _amount = balances[_redeemer];
        uint256 _feeShare = this.balance * _amount / supply;
        uint256 _reputationShare = _reputationSupply * _amount / supply;
        burn(_redeemer, _amount);
        _reputationToken.transfer(_redeemer, _reputationShare);
        require(_redeemer.call.value(_feeShare)());
        return true;
    }

    function contribute(address _participant, uint256 _amount) public onlyInGoodTimes returns (bool) {
        require(IMarket(msg.sender) == market);
        _amount = _amount.min(size - totalSupply());
        if (_amount == 0) {
            return;
        }
        market.getReputationToken().transferFrom(_participant, this, _amount);
        feeWindow.buy(_amount);
        mint(_participant, _amount);
        if (totalSupply() == size) {
            market.finishedCrowdsourcingDisputeBond();
        }
        return true;
    }

    function fork() public onlyInGoodTimes returns (bool) {
        require(IMarket(msg.sender) == market);
        IUniverse _newUniverse = market.getUniverse().createChildUniverse(payoutDistributionHash);
        IReputationToken _reputationToken = market.getReputationToken();
        IReputationToken _newReputationToken = _newUniverse.getReputationToken();
        uint256 _balance = _reputationToken.balanceOf(this);
        _reputationToken.migrateOut(_newReputationToken, _balance);
        _newReputationToken.mintForDisputeCrowdsourcer(_balance);
        // by removing the market, the token will become disavowed and therefore users can remove freely
        market = IMarket(0);
    }

    function disavow() public onlyInGoodTimes returns (bool) {
        require(IMarket(msg.sender) == market);
        market = IMarket(0);
        return true;
    }

    function getStake() public view returns (uint256) {
        return totalSupply();
    }

    function isDisavowed() public returns (bool) {
        return market == IMarket(0);
    }
}
