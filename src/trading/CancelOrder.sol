/**
 * Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE
 */

pragma solidity ^0.4.13;

import 'ROOT/trading/ICancelOrder.sol';
import 'ROOT/Controlled.sol';
import 'ROOT/libraries/ReentrancyGuard.sol';
import 'ROOT/trading/Order.sol';
import 'ROOT/reporting/IMarket.sol';
import 'ROOT/trading/ICash.sol';
import 'ROOT/trading/IOrders.sol';


/**
 * @title CancelOrder
 * @dev This allows you to cancel orders on the book.
 */
contract CancelOrder is Controlled, ReentrancyGuard, ICancelOrder {
    /**
     * @dev Cancellation: cancels an order, if a bid refunds money, if an ask returns shares
     * @return true if successful; throw on failure
     */
    function cancelOrder(bytes32 _orderId, Order.TradeTypes _type, IMarket _market, uint8 _outcome) nonReentrant external returns (bool) {
        require(_orderId != bytes32(0));
        require(_market.getTypeName() == "Market");

        // Look up the order the sender wants to cancel
        IOrders _orders = IOrders(controller.lookup("Orders"));
        uint256 _moneyEscrowed = _orders.getOrderMoneyEscrowed(_orderId);
        uint256 _sharesEscrowed = _orders.getOrderSharesEscrowed(_orderId);

        // Check that the order ID is correct and that the sender owns the order
        require(msg.sender == _orders.getOrderMaker(_orderId));

        // Clear the order first
        _orders.removeOrder(_orderId);

        refundOrder(msg.sender, _type, _sharesEscrowed, _moneyEscrowed, _market, _outcome);

        _orders.cancelOrderLog(_orderId);

        return true;
    }

    /**
     * @dev Issue refunds
     */
    function refundOrder(address _sender, Order.TradeTypes _type, uint256 _sharesEscrowed, uint256 _moneyEscrowed, IMarket _market, uint8 _outcome) private returns (bool) {
        if (_sharesEscrowed > 0) {
            // Return to user sharesEscrowed that weren't filled yet for all outcomes except the order outcome
            if (_type == Order.TradeTypes.Bid) {
                for (uint8 _i = 0; _i < _market.getNumberOfOutcomes(); ++_i) {
                    if (_i != _outcome) {
                        _market.getShareToken(_i).transfer(_sender, _sharesEscrowed);
                    }
                }
            // Shares refund if has shares escrowed for this outcome
            } else if (_type == Order.TradeTypes.Ask) {
                _market.getShareToken(_outcome).transfer(_sender, _sharesEscrowed);
            // unexpected type
            } else {
                throw;
            }
        }

        // Return to user moneyEscrowed that wasn't filled yet
        if (_moneyEscrowed > 0) {
            ICash _denominationToken = _market.getDenominationToken();
            require(_denominationToken.transferFrom(_market, _sender, _moneyEscrowed));
        }

        return true;
    }
}
