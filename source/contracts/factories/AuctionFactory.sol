pragma solidity 0.4.24;

import 'libraries/CloneFactory.sol';
import 'IController.sol';
import 'reporting/IUniverse.sol';
import 'reporting/Auction.sol';
import 'reporting/IReputationToken.sol';


contract AuctionFactory is CloneFactory {
    function createAuction(IController _controller, IUniverse _universe, IReputationToken _reputationToken) public returns (IAuction) {
        IAuction _auction = IAuction(createClone(_controller.lookup("Auction")));
        IControlled(_auction).setController(_controller);
        _auction.initialize(_universe, _reputationToken);
        return _auction;
    }
}
