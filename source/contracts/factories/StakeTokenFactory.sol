pragma solidity 0.4.17;


import 'libraries/Delegator.sol';
import 'reporting/IStakeToken.sol';
import 'reporting/IMarket.sol';
import 'IController.sol';


contract StakeTokenFactory {
    function createStakeToken(IController _controller, IMarket _market, uint256[] _payoutNumerators, bool _invalid) public returns (IStakeToken) {
        Delegator _delegator = new Delegator(_controller, "StakeToken");
        IStakeToken _stakeToken = IStakeToken(_delegator);
        _stakeToken.initialize(_market, _payoutNumerators, _invalid);
        return _stakeToken;
    }
}
