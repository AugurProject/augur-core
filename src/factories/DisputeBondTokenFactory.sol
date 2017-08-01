pragma solidity ^0.4.11;

import 'ROOT/libraries/Delegator.sol';


// FIXME: remove once this can be imported as a solidty contract
contract DisputeBondToken {
    function initialize(address market, address bondHolder, uint256 bondAmount, int256 payoutDistributionHash);
}


contract DisputeBondTokenFactory {

    function createDisputeBondToken(address controller, address market, address bondHolder, uint256 bondAmount, int256 payoutDistributionHash) returns (DisputeBondToken) {
        Delegator del = new Delegator(controller, "disputeBondToken");
        DisputeBondToken disputeBondToken = DisputeBondToken(del);
        disputeBondToken.initialize(market, bondHolder, bondAmount, payoutDistributionHash);
        return disputeBondToken;
    }
}