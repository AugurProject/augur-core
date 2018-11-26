pragma solidity 0.4.24;

import 'IController.sol';
import 'reporting/IUniverse.sol';


contract IUniverseFactory {
    function createUniverse(IController _controller, IUniverse _parentUniverse, bytes32 _parentPayoutDistributionHash) public returns (IUniverse);
}
