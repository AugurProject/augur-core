pragma solidity 0.4.18;


import '../libraries/ITyped.sol';
import '../reporting/IMarket.sol';
import '../libraries/IOwnable.sol';


contract IDisputeBond is ITyped, IOwnable {
    function initialize(IMarket _market, address _bondHolder, uint256 _bondAmount, bytes32 _payoutDistributionHash) public returns (bool);
    function getMarket() constant public returns (IMarket);
    function getDisputedPayoutDistributionHash() constant public returns (bytes32);
    function getBondRemainingToBePaidOut() constant public returns (uint256);
}
