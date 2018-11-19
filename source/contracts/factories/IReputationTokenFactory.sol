pragma solidity 0.4.24;

import 'IController.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReputationToken.sol';


contract IReputationTokenFactory {
    function createReputationToken(IController _controller, IUniverse _universe, IUniverse _parentUniverse) public returns (IReputationToken);
}
