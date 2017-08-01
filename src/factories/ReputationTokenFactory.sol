pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/Controller.sol';


// FIXME: remove once this can be imported as a solidty contract
contract Branch {
    function stub() {}
}


// FIXME: remove once this can be imported as a solidty contract
contract ReputationToken {
    function initialize(Branch _branch);
}


contract ReputationTokenFactory {
    function createReputationToken(Controller _controller, Branch _branch) returns (ReputationToken) {
        Delegator _delegator = new Delegator(_controller, "ReputationToken");
        ReputationToken _reputationToken = ReputationToken(_delegator);
        _reputationToken.initialize(_branch);
        return _reputationToken;
    }
}