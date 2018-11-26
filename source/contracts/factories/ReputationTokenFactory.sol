pragma solidity 0.4.24;


import 'IController.sol';
import 'reporting/IUniverse.sol';
import 'reporting/ReputationToken.sol';


contract ReputationTokenFactory {
    function createReputationToken(IController _controller, IUniverse _universe, IUniverse _parentUniverse) public returns (IReputationToken) {
        return IReputationToken(new ReputationToken(_controller, _universe, _parentUniverse));
    }
}
