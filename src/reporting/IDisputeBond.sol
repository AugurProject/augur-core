pragma solidity ^0.4.13;

import 'ROOT/libraries/Typed.sol';
import 'ROOT/reporting/IMarket.sol';


contract IDisputeBond is Typed {
    function initialize(IMarket _market, address _bondHolder, uint256 _bondAmount, bytes32 _payoutDistributionHash) public returns (bool);
    function getMarket() constant public returns (IMarket);
    function getDisputedPayoutDistributionHash() constant public returns (bytes32);
    function getBondRemainingToBePaidOut() constant public returns (uint256);
}
