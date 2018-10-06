pragma solidity 0.4.24;

import 'libraries/Delegator.sol';
import 'IController.sol';
import 'reporting/IAuction.sol';
import 'reporting/IAuctionToken.sol';
import 'libraries/token/ERC20.sol';


contract AuctionTokenFactory {
    function createAuctionToken(IController _controller, IAuction _auction, ERC20 _redemptionToken, uint256 _auctionIndex) public returns (IAuctionToken) {
        Delegator _delegator = new Delegator(_controller, "AuctionToken");
        IAuctionToken _auctionToken = IAuctionToken(_delegator);
        _auctionToken.initialize(_auction, _redemptionToken, _auctionIndex);
        return _auctionToken;
    }
}
