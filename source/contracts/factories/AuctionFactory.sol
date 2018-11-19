pragma solidity 0.4.24;

import 'IController.sol';
import 'reporting/IUniverse.sol';
import 'reporting/Auction.sol';
import 'reporting/IReputationToken.sol';


contract AuctionFactory {
    function createAuction(IController _controller, IUniverse _universe, IReputationToken _reputationToken) public returns (IAuction) {
        return IAuction(new Auction(_controller, _universe, _reputationToken));
    }
}
