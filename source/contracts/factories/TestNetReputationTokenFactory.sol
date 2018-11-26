pragma solidity 0.4.24;


import 'IController.sol';
import 'reporting/IUniverse.sol';
import 'TestNetReputationToken.sol';


contract TestNetReputationTokenFactory {
    function createReputationToken(IController _controller, IUniverse _universe, IUniverse _parentUniverse) public returns (IReputationToken) {
        IReputationToken _reputationToken = IReputationToken(new TestNetReputationToken(_controller, _universe, _parentUniverse));
        return _reputationToken;
    }
}
