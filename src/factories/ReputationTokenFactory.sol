pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/Controller.sol';
import 'ROOT/reporting/Branch.sol';
import 'ROOT/reporting/ReputationToken.sol';


contract ReputationTokenFactory {
    function createReputationToken(Controller _controller, Branch _branch) returns (ReputationToken) {
        Delegator _delegator = new Delegator(_controller, "ReputationToken");
        ReputationToken _reputationToken = ReputationToken(_delegator);
        _reputationToken.initialize(_branch);
        return _reputationToken;
    }
}
