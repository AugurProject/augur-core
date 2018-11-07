pragma solidity 0.4.24;


import 'libraries/CloneFactory.sol';
import 'IController.sol';
import 'IControlled.sol';
import 'reporting/IUniverse.sol';


contract UniverseFactory is CloneFactory {
    function createUniverse(IController _controller, IUniverse _parentUniverse, bytes32 _parentPayoutDistributionHash) public returns (IUniverse) {
        IUniverse _universe = IUniverse(createClone(_controller.lookup("Universe")));
        IControlled(_universe).setController(_controller);
        _universe.initialize(_parentUniverse, _parentPayoutDistributionHash);
        return _universe;
    }
}
