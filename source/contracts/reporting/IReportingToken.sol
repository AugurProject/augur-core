pragma solidity 0.4.17;


import 'libraries/Typed.sol';
import 'libraries/token/ERC20.sol';
import 'reporting/IMarket.sol';


contract IReportingToken is Typed, ERC20 {
    function initialize(IMarket _market, uint256[] _payoutNumerators) public returns (bool);
    function getMarket() public constant returns (IMarket);
    function getPayoutNumerator(uint8 index) public constant returns (uint256);
    function getPayoutDistributionHash() public constant returns (bytes32);
    function isValid() public constant returns (bool);
}
