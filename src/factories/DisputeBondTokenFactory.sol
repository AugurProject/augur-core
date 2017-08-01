pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/Controller.sol';


// FIXME: remove once this can be imported as a solidty contract
contract Market {
    function stub() {}
}


// FIXME: remove once this can be imported as a solidty contract
contract DisputeBondToken {
    function initialize(Market _market, address _bondHolder, uint256 _bondAmount, int256 _payoutDistributionHash);
}


contract DisputeBondTokenFactory {
    function createDisputeBondToken(Controller _controller, Market _market, address _bondHolder, uint256 _bondAmount, int256 _payoutDistributionHash) returns (DisputeBondToken) {
        Delegator _delegator = new Delegator(_controller, "disputeBondToken");
        DisputeBondToken _disputeBondToken = DisputeBondToken(_delegator);
        _disputeBondToken.initialize(_market, _bondHolder, _bondAmount, _payoutDistributionHash);
        return _disputeBondToken;
    }
}