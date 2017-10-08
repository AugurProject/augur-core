pragma solidity 0.4.17;
pragma experimental ABIEncoderV2;
pragma experimental "v0.5.0";

import 'trading/Order.sol';
import 'reporting/IMarket.sol';


contract ICreateOrder {
    function publicCreateOrder(Order.TradeTypes, uint256, uint256, IMarket, uint8, bytes32, bytes32, uint256) external payable returns (bytes32);
    function createOrder(address, Order.TradeTypes, uint256, uint256, IMarket, uint8, bytes32, bytes32, uint256) external returns (bytes32);
}
