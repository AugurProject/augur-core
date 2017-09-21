pragma solidity ^0.4.13;

import 'ROOT/trading/ICash.sol';
import 'ROOT/Controlled.sol';
import 'ROOT/Augur.sol';


/**
 * @title Provides modifiers which take care of Cash/ETH conversion
 */
contract CashAutoConverter is Controlled {
    /**
     * @dev Convert any ETH provided in the transaction into Cash before the function executes
     */
    modifier convertToCash() {
        ethToCash();
        _;
        cashToETH();
    }

    /**
     * @dev Withdraw any Cash held by the sender into ETH and transfer it to them after the function executes
     */
    modifier convertFromCash() {
        _;
        cashToETH();
    }

    function ethToCash() payable public returns (bool) {
        if (msg.value > 0) {
            ICash(controller.lookup("Cash")).depositEtherFor.value(msg.value)(msg.sender);
        }
        return true;
    }

    function cashToETH() public returns (bool) {
        ICash _cash = ICash(controller.lookup("Cash"));
        uint256 _tokenBalance = _cash.balanceOf(msg.sender);
        if (_tokenBalance > 0) {
            Augur(controller.lookup("Augur")).trustedTransfer(_cash, msg.sender, this, _tokenBalance);
            _cash.withdrawEtherTo(msg.sender, _tokenBalance);
        }
        return true;
    }
}
