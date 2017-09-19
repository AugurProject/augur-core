pragma solidity ^0.4.13;

import 'ROOT/trading/Cash.sol';
import 'ROOT/Controlled.sol';



/**
 * @title Provides modifiers which take care of Cash/ETH conversion
 */
contract CashWrapper is Controlled {
    /**
     * @dev Convert any ETH provided in the transaction into Cash before the function executes
     */
    modifier convertToCash() {
        ethToCash();
        _;
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
            Cash _cash = Cash(controller.lookup("Cash"));
            _cash.depositEther.value(msg.value)();
            _cash.transfer(msg.sender, msg.value);
        }
        return true;
    }

    function cashToETH() public returns (bool) {
        Cash _cash = Cash(controller.lookup("Cash"));
        uint256 _tokenBalance = _cash.balanceOf(msg.sender);
        if (_tokenBalance > 0) {
            _cash.transferFrom(msg.sender, this, _tokenBalance);
            _cash.withdrawEtherTo(msg.sender, _tokenBalance);
        }
        return true;
    }
}
