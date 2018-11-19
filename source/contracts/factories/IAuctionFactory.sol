pragma solidity 0.4.24;

import 'IController.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReputationToken.sol';


contract IAuctionFactory {
    function createAuction(IController _controller, IUniverse _universe, IReputationToken _reputationToken) public returns (IAuction);
}
