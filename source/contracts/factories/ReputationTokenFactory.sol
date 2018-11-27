pragma solidity 0.4.24;


import 'IController.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IV2ReputationToken.sol';
import 'reporting/ReputationToken.sol';


contract ReputationTokenFactory {
    function createReputationToken(IController _controller, IUniverse _universe, IUniverse _parentUniverse) public returns (IV2ReputationToken) {
        return IV2ReputationToken(new ReputationToken(_controller, _universe, _parentUniverse));
    }
}
