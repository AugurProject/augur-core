/**
 * Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE
 */

pragma solidity 0.4.20;


import 'trading/ICancelOrder.sol';
import 'Controlled.sol';
import 'libraries/ReentrancyGuard.sol';
import 'libraries/CashAutoConverter.sol';
import 'trading/Order.sol';
import 'reporting/IMarket.sol';
import 'trading/ICash.sol';
import 'trading/IOrders.sol';


/**
 * @title CancelOrder
 * @dev This allows you to cancel orders on the book.
 */
contract CancelOrder is CashAutoConverter, ReentrancyGuard, ICancelOrder {
    /**
     * @dev Cancellation: cancels an order, if a bid refunds money, if an ask returns shares
     * @return true if successful; throw on failure
     */
    function cancelOrder(bytes32 _orderId) nonReentrant convertToAndFromCash external returns (bool) {
        require(_orderId != bytes32(0));

        // Look up the order the sender wants to cancel
        IOrders _orders = IOrders(controller.lookup("Orders"));
        uint256 _moneyEscrowed = _orders.getOrderMoneyEscrowed(_orderId);
        uint256 _sharesEscrowed = _orders.getOrderSharesEscrowed(_orderId);
        Order.Types _type = _orders.getOrderType(_orderId);
        IMarket _market = _orders.getMarket(_orderId);
        uint256 _outcome = _orders.getOutcome(_orderId);

        // Check that the order ID is correct and that the sender owns the order
        require(msg.sender == _orders.getOrderCreator(_orderId));

        // Clear the order first
        _orders.removeOrder(_orderId);

        refundOrder(msg.sender, _type, _sharesEscrowed, _moneyEscrowed, _market, _outcome);
        _orders.decrementTotalEscrowed(_market, _moneyEscrowed);
        _market.assertBalances();

        controller.getAugur().logOrderCanceled(_market.getUniverse(), _market.getShareToken(_outcome), msg.sender, _orderId, _type, _moneyEscrowed, _sharesEscrowed);

        return true;
    }

    /**
     * @dev Issue refunds
     */
    function refundOrder(address _sender, Order.Types _type, uint256 _sharesEscrowed, uint256 _moneyEscrowed, IMarket _market, uint256 _outcome) private returns (bool) {
        if (_sharesEscrowed > 0) {
            // Return to user sharesEscrowed that weren't filled yet for all outcomes except the order outcome
            if (_type == Order.Types.Bid) {
                for (uint256 _i = 0; _i < _market.getNumberOfOutcomes(); ++_i) {
                    if (_i != _outcome) {
                        _market.getShareToken(_i).trustedCancelOrderTransfer(_market, _sender, _sharesEscrowed);
                    }
                }
            // Shares refund if has shares escrowed for this outcome
            } else {
                _market.getShareToken(_outcome).trustedCancelOrderTransfer(_market, _sender, _sharesEscrowed);
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
