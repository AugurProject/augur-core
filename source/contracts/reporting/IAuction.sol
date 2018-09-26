pragma solidity 0.4.24;

import 'reporting/IUniverse.sol';
import 'reporting/IRepPriceOracle.sol';

contract IAuction is IRepPriceOracle {
    function initialize(IUniverse _universe) public returns (bool);
    function getCurrentOfferedPrice() public view returns (uint256);
    function take(uint256 _amount) public returns (bool);
}
