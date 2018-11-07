pragma solidity 0.4.24;


import 'libraries/CloneFactory.sol';
import 'IController.sol';
import 'IControlled.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReputationToken.sol';


contract ReputationTokenFactory is CloneFactory {
    function createReputationToken(IController _controller, IUniverse _universe) public returns (IReputationToken) {
        IReputationToken _reputationToken = IReputationToken(createClone(_controller.lookup("ReputationToken")));
        IControlled(_reputationToken).setController(_controller);
        _reputationToken.initialize(_universe);
        return _reputationToken;
    }
}
