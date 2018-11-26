pragma solidity 0.4.24;

import 'IController.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IRepPriceOracle.sol';
import 'reporting/IAuctionToken.sol';
import 'reporting/IReputationToken.sol';


contract IAuction is IRepPriceOracle {
    IAuctionToken public repAuctionToken; // The token keeping track of ETH provided to purchase the REP being auctioned off
    IAuctionToken public ethAuctionToken; // The token keeping track of REP provided to purchase the ETH being auctioned off
    function initialize(IUniverse _universe, IReputationToken _reputationToken) public returns (bool);
    function recordFees(uint256 _feeAmount) public returns (bool);
    function getUniverse() public view returns (IUniverse);
    function getAuctionIndexForCurrentTime() public view returns (uint256);
}
