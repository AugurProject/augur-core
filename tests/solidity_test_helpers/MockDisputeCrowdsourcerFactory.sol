pragma solidity 0.4.18;

import 'reporting/IDisputeCrowdsourcer.sol';
import 'reporting/IMarket.sol';
import 'IController.sol';


contract MockDisputeCrowdsourcerFactory {
    IDisputeCrowdsourcer private disputeCrowdsourcer;

    function setDisputeCrowdsourcer(IDisputeCrowdsourcer _disputeCrowdsourcer) public returns (bool) {
        disputeCrowdsourcer = _disputeCrowdsourcer;
    }

    function createDisputeCrowdsourcer(IController _controller, IMarket _market, uint256 _size, bytes32 _payoutDistributionHash, uint256[] _payoutNumerators, bool _invalid) public returns (IDisputeCrowdsourcer) {
        return disputeCrowdsourcer;
    }
}