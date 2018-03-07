pragma solidity 0.4.20;

import 'reporting/IMarket.sol';
import 'IController.sol';
import 'reporting/IDisputeCrowdsourcer.sol';
import 'TEST/MockDisputeCrowdsourcer.sol';


contract MockDisputeCrowdsourcerFactory {
    MockDisputeCrowdsourcer private disputeCrowdsourcer;
    bytes32 private createdPayoutDistributionHashValue;
    uint256[] private createdPayoutNumeratorsValue;

    function setDisputeCrowdsourcer(MockDisputeCrowdsourcer _disputeCrowdsourcer) public returns (bool) {
        disputeCrowdsourcer = _disputeCrowdsourcer;
    }

    function getDisputeCrowdsourcer() public returns (MockDisputeCrowdsourcer) {
        return disputeCrowdsourcer;
    }

    function getCreatedPayoutDistributionHash() public returns(bytes32) {
        return createdPayoutDistributionHashValue;
    }

    function getCreatedPayoutNumerators() public returns(uint256[]) {
        return createdPayoutNumeratorsValue;
    }

    function createDisputeCrowdsourcer(IController _controller, IMarket _market, uint256 _size, bytes32 _payoutDistributionHash, uint256[] _payoutNumerators, bool _invalid) public returns (IDisputeCrowdsourcer) {
        createdPayoutDistributionHashValue = _payoutDistributionHash;
        createdPayoutNumeratorsValue = _payoutNumerators;
        // set for later testing use
        disputeCrowdsourcer.setPayoutDistributionHash(_payoutDistributionHash);
        disputeCrowdsourcer.setPayoutNumeratorsValue(_payoutNumerators);
        return disputeCrowdsourcer;
    }
}
