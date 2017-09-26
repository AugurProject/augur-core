pragma solidity ^0.4.13;

import 'ROOT/libraries/Typed.sol';
import 'ROOT/libraries/token/ERC20.sol';
import 'ROOT/reporting/IMarket.sol';


contract IReportingToken is Typed, ERC20 {
    function initialize(IMarket _market, uint256[] _payoutNumerators) public returns (bool);
    function getMarket() public constant returns (IMarket);
    function getPayoutNumerator(uint8 index) public constant returns (uint256);
    function getPayoutDistributionHash() public constant returns (bytes32);
}
