pragma solidity ^0.4.13;

import 'ROOT/trading/Order.sol';
import 'ROOT/reporting/IMarket.sol';


contract IMakeOrder {
    function publicMakeOrder(Order.TradeTypes, uint256, uint256, IMarket, uint8, bytes32, bytes32, uint256) public returns (bytes32);
    function makeOrder(address, Order.TradeTypes, uint256, uint256, IMarket, uint8, bytes32, bytes32, uint256) public returns (bytes32);
}
