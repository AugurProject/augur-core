pragma solidity 0.4.18;


import 'libraries/Delegator.sol';
import 'reporting/IDisputeBond.sol';
import 'reporting/IMarket.sol';
import 'IController.sol';


contract DisputeBondFactory {
    function createDisputeBond(IController _controller, IMarket _market, address _bondHolder, uint256 _bondAmount, bytes32 _payoutDistributionHash) public returns (IDisputeBond) {
        Delegator _delegator = new Delegator(_controller, "DisputeBond");
        IDisputeBond _disputeBond = IDisputeBond(_delegator);
        _disputeBond.initialize(_market, _bondHolder, _bondAmount, _payoutDistributionHash);
        return _disputeBond;
    }
}
