pragma solidity 0.4.24;

import 'reporting/IReputationToken.sol';


contract IV2ReputationToken is IReputationToken {
    function trustedAuctionTransfer(address _source, address _destination, uint256 _attotokens) public returns (bool);
    function mintForAuction(uint256 _amountToMint) public returns (bool);
    function burnForAuction(uint256 _amountToMint) public returns (bool);
    function burnForMarket(uint256 _amountToBurn) public returns (bool);
}
