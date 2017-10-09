pragma solidity ^0.4.17;

import 'libraries/Typed.sol';
import 'reporting/IMarket.sol';


contract IDisputeBond is Typed {
    function initialize(IMarket _market, address _bondHolder, uint256 _bondAmount, bytes32 _payoutDistributionHash) public returns (bool);
    function getMarket() constant public returns (IMarket);
    function getDisputedPayoutDistributionHash() constant public returns (bytes32);
    function getBondRemainingToBePaidOut() constant public returns (uint256);
}
