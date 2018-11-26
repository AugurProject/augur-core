pragma solidity 0.4.24;

import 'IController.sol';
import 'reporting/Universe.sol';


contract UniverseFactory {
    function createUniverse(IController _controller, IUniverse _parentUniverse, bytes32 _parentPayoutDistributionHash) public returns (IUniverse) {
        return IUniverse(new Universe(_controller, _parentUniverse, _parentPayoutDistributionHash));
    }
}
