pragma solidity 0.4.20;

import 'reporting/IDisputeCrowdsourcer.sol';
import 'libraries/token/VariableSupplyToken.sol';
import 'reporting/BaseReportingParticipant.sol';
import 'libraries/Initializable.sol';
import 'libraries/DelegationTarget.sol';
import 'reporting/IUniverse.sol';


contract DisputeCrowdsourcer is DelegationTarget, VariableSupplyToken, BaseReportingParticipant, IDisputeCrowdsourcer, Initializable {
    IUniverse internal universe;

    function initialize(IMarket _market, uint256 _size, bytes32 _payoutDistributionHash, uint256[] _payoutNumerators, bool _invalid) public onlyInGoodTimes beforeInitialized returns (bool) {
        endInitialization();
        market = _market;
        universe = market.getUniverse();
        reputationToken = market.getReputationToken();
        feeWindow = market.getFeeWindow();
        cash = market.getDenominationToken();
        size = _size;
        payoutNumerators = _payoutNumerators;
        payoutDistributionHash = _payoutDistributionHash;
        invalid = _invalid;
        return true;
    }

    function redeem(address _redeemer) public onlyInGoodTimes returns (bool) {
        bool _isDisavowed = isDisavowed();
        if (!_isDisavowed && !market.isFinalized()) {
            market.finalize();
        }
        redeemForAllFeeWindows();
        uint256 _reputationSupply = reputationToken.balanceOf(this);
        uint256 _cashSupply = cash.balanceOf(this);
        uint256 _supply = totalSupply();
        uint256 _amount = balances[_redeemer];
        uint256 _feeShare = _cashSupply.mul(_amount).div(_supply);
        uint256 _reputationShare = _reputationSupply.mul(_amount).div(_supply);
        burn(_redeemer, _amount);
        require(reputationToken.transfer(_redeemer, _reputationShare));
        if (_feeShare > 0) {
            cash.withdrawEtherTo(_redeemer, _feeShare);
        }
        controller.getAugur().logDisputeCrowdsourcerRedeemed(universe, _redeemer, market, _amount, _reputationShare, _feeShare, payoutNumerators);
        return true;
    }

    function contribute(address _participant, uint256 _amount) public onlyInGoodTimes returns (uint256) {
        require(IMarket(msg.sender) == market);
        _amount = _amount.min(size.sub(totalSupply()));
        if (_amount == 0) {
            return 0;
        }
        reputationToken.trustedReportingParticipantTransfer(_participant, this, _amount);
        feeWindow.mintFeeTokens(_amount);
        mint(_participant, _amount);
        assert(reputationToken.balanceOf(this) >= totalSupply());
        return _amount;
    }

    function withdrawInEmergency() public onlyInBadTimes returns (bool) {
        uint256 _reputationSupply = reputationToken.balanceOf(this);
        uint256 _attotokens = balances[msg.sender];
        uint256 _supply = totalSupply();
        uint256 _reputationShare = _reputationSupply.mul(_attotokens).div(_supply);
        burn(msg.sender, _attotokens);
        if (_reputationShare != 0) {
            require(reputationToken.transfer(msg.sender, _reputationShare));
        }
        return true;
    }

    function forkAndRedeem() public onlyInGoodTimes returns (bool) {
        fork();
        redeem(msg.sender);
        return true;
    }

    function getStake() public view returns (uint256) {
        return totalSupply();
    }

    function onTokenTransfer(address _from, address _to, uint256 _value) internal returns (bool) {
        controller.getAugur().logDisputeCrowdsourcerTokensTransferred(universe, _from, _to, _value);
        return true;
    }

    function onMint(address _target, uint256 _amount) internal returns (bool) {
        controller.getAugur().logDisputeCrowdsourcerTokensMinted(universe, _target, _amount);
        return true;
    }

    function onBurn(address _target, uint256 _amount) internal returns (bool) {
        controller.getAugur().logDisputeCrowdsourcerTokensBurned(universe, _target, _amount);
        return true;
    }

    function getFeeWindow() public view returns (IFeeWindow) {
        return feeWindow;
    }

    function getReputationToken() public view returns (IReputationToken) {
        return reputationToken;
    }
}
