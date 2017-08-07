pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/Controller.sol';
import 'ROOT/reporting/Interfaces.sol';


contract ReputationTokenFactory {
    function createReputationToken(Controller _controller, IBranch _branch) returns (IReputationToken) {
        Delegator _delegator = new Delegator(_controller, "ReputationToken");
        IReputationToken _reputationToken = IReputationToken(_delegator);
        _reputationToken.initialize(_branch);
        return _reputationToken;
    }
}
