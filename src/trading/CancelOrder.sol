/**
 * Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE
 */

pragma solidity ^0.4.13;

import 'ROOT/Controller.sol';
import 'ROOT/libraries/ReentrancyGuard.sol';
import 'ROOT/libraries/Trading.sol';
import 'ROOT/trading/Cash.sol';
import 'ROOT/trading/Orders.sol';


/**
 * @title CancelOrder
 * @dev This allows you to cancel orders on the book.
 */
contract CancelOrder is Controlled, ReentrancyGuard {
    /**
     * @dev Cancellation: cancels an order, if a bid refunds money, if an ask returns shares
     * @return true if successful; throw on failure
     */
    function cancelOrder(bytes32 _orderId, Trading.TradeTypes _type, Market _market, uint8 _outcome) nonReentrant external returns (bool) {
        require(_orderId != bytes32(0));
        require(_market.getTypeName() == "Market");

        // Look up the order the sender wants to cancel
        Orders _orders = Orders(controller.lookup("Orders"));
        uint256 _fxpMoneyEscrowed = _orders.getOrderMoneyEscrowed(_orderId, _type, _market, _outcome);
        uint256 _fxpSharesEscrowed = _orders.getOrderSharesEscrowed(_orderId, _type, _market, _outcome);

        // Check that the order ID is correct and that the sender owns the order
        require(msg.sender == _orders.getOrderOwner(_orderId, _type, _market, _outcome));

        // Clear the order first
        _orders.removeOrder(_orderId, _type, _market, _outcome);

        refundOrder(msg.sender, _type, _fxpSharesEscrowed, _fxpMoneyEscrowed, _market, _outcome);

        _orders.cancelOrderLog(_market, msg.sender, _orders.getPrice(_orderId, _type, _market, _outcome), _orders.getAmount(_orderId, _type, _market, _outcome), _orderId, _outcome, _type, _fxpMoneyEscrowed, _fxpSharesEscrowed);

        return true;
    }

    /**
     * @dev Issue refunds
     */
    function refundOrder(address _sender, Trading.TradeTypes _type, uint256 _fxpSharesEscrowed, uint256 _fxpMoneyEscrowed, Market _market, uint8 _outcome) private returns (bool) {
        if (_fxpSharesEscrowed > 0) {
            // Return to user sharesEscrowed that weren't filled yet for all outcomes except the order outcome
            if (_type == Trading.TradeTypes.Bid) {
                for (uint8 _i = 0; _i < _market.getNumberOfOutcomes(); ++_i) {
                    if (_i != _outcome) {
                        _market.getShareToken(_i).transfer(_sender, _fxpSharesEscrowed);
                    }
                }
            // Shares refund if has shares escrowed for this outcome
            } else if (_type == Trading.TradeTypes.Ask) {
                _market.getShareToken(_outcome).transfer(_sender, _fxpSharesEscrowed);
            // unexpected type
            } else {
                throw;
            }
        }

        // Return to user moneyEscrowed that wasn't filled yet
        if (_fxpMoneyEscrowed > 0) {
            Cash _denominationToken = _market.getDenominationToken();
            require(_denominationToken.transferFrom(_market, _sender, _fxpMoneyEscrowed));
        }

        return true;
    }
}
