pragma solidity 0.4.17;
pragma experimental ABIEncoderV2;
pragma experimental "v0.5.0";

import 'libraries/Delegator.sol';
import 'IController.sol';
import 'reporting/IUniverse.sol';


contract UniverseFactory {
    function createUniverse(IController _controller, IUniverse _parentUniverse, bytes32 _parentPayoutDistributionHash) returns (IUniverse) {
        Delegator _delegator = new Delegator(_controller, "Universe");
        IUniverse _universe = IUniverse(_delegator);
        _universe.initialize(_parentUniverse, _parentPayoutDistributionHash);
        return _universe;
    }
}
