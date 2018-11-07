pragma solidity 0.4.24;

import 'libraries/CloneFactory.sol';
import 'reporting/IDisputeCrowdsourcer.sol';
import 'reporting/IMarket.sol';
import 'IController.sol';
import 'IControlled.sol';


contract DisputeCrowdsourcerFactory is CloneFactory {
    function createDisputeCrowdsourcer(IController _controller, IMarket _market, uint256 _size, bytes32 _payoutDistributionHash, uint256[] _payoutNumerators) public returns (IDisputeCrowdsourcer) {
        IDisputeCrowdsourcer _disputeCrowdsourcer = IDisputeCrowdsourcer(createClone(_controller.lookup("DisputeCrowdsourcer")));
        IControlled(_disputeCrowdsourcer).setController(_controller);
        _disputeCrowdsourcer.initialize(_market, _size, _payoutDistributionHash, _payoutNumerators);
        return _disputeCrowdsourcer;
    }
}
