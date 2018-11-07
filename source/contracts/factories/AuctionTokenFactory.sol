pragma solidity 0.4.24;

import 'libraries/CloneFactory.sol';
import 'IController.sol';
import 'reporting/IAuction.sol';
import 'reporting/IAuctionToken.sol';
import 'libraries/token/ERC20.sol';
import 'IControlled.sol';


contract AuctionTokenFactory is CloneFactory {
    function createAuctionToken(IController _controller, IAuction _auction, ERC20 _redemptionToken, uint256 _auctionIndex) public returns (IAuctionToken) {
        IAuctionToken _auctionToken = IAuctionToken(createClone(_controller.lookup("AuctionToken")));
        IControlled(_auctionToken).setController(_controller);
        _auctionToken.initialize(_auction, _redemptionToken, _auctionIndex);
        return _auctionToken;
    }
}
