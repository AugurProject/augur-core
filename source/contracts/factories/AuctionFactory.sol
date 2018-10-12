pragma solidity 0.4.24;


import 'libraries/Delegator.sol';
import 'IController.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IAuction.sol';


contract AuctionFactory {
    function createAuction(IController _controller, IUniverse _universe) public returns (IAuction) {
        Delegator _delegator = new Delegator(_controller, "Auction");
        IAuction _Auction = IAuction(_delegator);
        _Auction.initialize(_universe);
        return _Auction;
    }
}
