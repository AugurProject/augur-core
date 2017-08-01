pragma solidity ^0.4.11;

import 'ROOT/libraries/Delegator.sol';


// FIXME: remove once this can be imported as a solidty contract
contract ShareToken {
    function initialize(address market, int256 outcome);
}


contract ShareTokenFactory {

    function createShareToken(address controller, address market, int256 outcome) returns (ShareToken) {
        Delegator del = new Delegator(controller, "shareToken");
        ShareToken shareToken = ShareToken(del);
        shareToken.initialize(market, outcome);
        return shareToken;
    }
}