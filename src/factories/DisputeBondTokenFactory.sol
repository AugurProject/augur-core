pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/reporting/IDisputeBond.sol';
import 'ROOT/reporting/IMarket.sol';
import 'ROOT/IController.sol';


contract DisputeBondTokenFactory {
    function createDisputeBondToken(IController _controller, IMarket _market, address _bondHolder, uint256 _bondAmount, bytes32 _payoutDistributionHash) returns (IDisputeBond) {
        Delegator _delegator = new Delegator(_controller, "DisputeBondToken");
        IDisputeBond _disputeBond = IDisputeBond(_delegator);
        _disputeBond.initialize(_market, _bondHolder, _bondAmount, _payoutDistributionHash);
        return _disputeBond;
    }
}
