pragma solidity 0.4.17;


import 'libraries/Delegator.sol';
import 'reporting/IDisputeBond.sol';
import 'reporting/IMarket.sol';
import 'IController.sol';


contract DisputeBondTokenFactory {
    function createDisputeBondToken(IController _controller, IMarket _market, address _bondHolder, uint256 _bondAmount, bytes32 _payoutDistributionHash) public returns (IDisputeBond) {
        Delegator _delegator = new Delegator(_controller, "DisputeBondToken");
        IDisputeBond _disputeBond = IDisputeBond(_delegator);
        _disputeBond.initialize(_market, _bondHolder, _bondAmount, _payoutDistributionHash);
        return _disputeBond;
    }
}
