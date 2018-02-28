pragma solidity 0.4.20;


import 'libraries/Delegator.sol';
import 'IController.sol';
import 'reporting/IUniverse.sol';


contract MockUniverseFactory {
    IUniverse private createUniverseParentUniverseValue;
    bytes32 private createUniverseParentPayoutDistributionHashValue;
    IUniverse private createUniverseUniverseValue;

    function setCreateUniverseUniverseValue(IUniverse _universe) public {
        createUniverseUniverseValue = _universe;
    }

    function getCreateUniverseParentUniverseValue() public returns(IUniverse) {
        return createUniverseParentUniverseValue;
    }

    function getCreateUniverseParentPayoutDistributionHashValue() public returns(bytes32) {
        return createUniverseParentPayoutDistributionHashValue;
    }

    function createUniverse(IController _controller, IUniverse _parentUniverse, bytes32 _parentPayoutDistributionHash) public returns (IUniverse) {
        createUniverseParentUniverseValue = _parentUniverse;
        createUniverseParentPayoutDistributionHashValue = _parentPayoutDistributionHash;
        return createUniverseUniverseValue;
    }
}
