pragma solidity 0.4.24;


import 'libraries/CloneFactory.sol';
import 'IController.sol';
import 'reporting/IUniverse.sol';
import 'reporting/Auction.sol';
import 'reporting/IReputationToken.sol';


contract AuctionFactory is CloneFactory {
    function createAuction(IController _controller, IUniverse _universe, IReputationToken _reputationToken) public returns (IAuction) {
        return IAuction(new Auction(_controller, _universe, _reputationToken));
    }
}
