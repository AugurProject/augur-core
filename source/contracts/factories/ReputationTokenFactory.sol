pragma solidity ^0.4.13;

import 'libraries/Delegator.sol';
import 'IController.sol';
import 'reporting/IBranch.sol';
import 'reporting/IReputationToken.sol';


contract ReputationTokenFactory {
    function createReputationToken(IController _controller, IBranch _branch) returns (IReputationToken) {
        Delegator _delegator = new Delegator(_controller, "ReputationToken");
        IReputationToken _reputationToken = IReputationToken(_delegator);
        _reputationToken.initialize(_branch);
        return _reputationToken;
    }
}
