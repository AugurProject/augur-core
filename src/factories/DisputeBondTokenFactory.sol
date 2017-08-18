pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/reporting/DisputeBondToken.sol';
import 'ROOT/reporting/Market.sol';
import 'ROOT/Controller.sol';


contract DisputeBondTokenFactory {
    function createDisputeBondToken(Controller _controller, Market _market, address _bondHolder, uint256 _bondAmount, bytes32 _payoutDistributionHash) returns (DisputeBondToken) {
        Delegator _delegator = new Delegator(_controller, "DisputeBondToken");
        DisputeBondToken _disputeBondToken = DisputeBondToken(_delegator);
        _disputeBondToken.initialize(_market, _bondHolder, _bondAmount, _payoutDistributionHash);
        return _disputeBondToken;
    }
}