pragma solidity ^0.4.11;

import 'ROOT/libraries/Delegator.sol';


// FIXME: remove once this can be imported as a solidty contract
contract ReputationToken {
    function initialize(address branch);
}


contract ReputationTokenFactory {

    function createReputationToken(address controller, address branch) returns (ReputationToken) {
        Delegator del = new Delegator(controller, "ReputationToken");
        ReputationToken reputationToken = ReputationToken(del);
        reputationToken.initialize(branch);
        return reputationToken;
    }
}