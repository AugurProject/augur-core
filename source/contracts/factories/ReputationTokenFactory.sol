pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/IController.sol';
import 'ROOT/reporting/IBranch.sol';
import 'ROOT/reporting/IReputationToken.sol';


contract ReputationTokenFactory {
    function createReputationToken(IController _controller, IBranch _branch) returns (IReputationToken) {
        Delegator _delegator = new Delegator(_controller, "ReputationToken");
        IReputationToken _reputationToken = IReputationToken(_delegator);
        _reputationToken.initialize(_branch);
        return _reputationToken;
    }
}
