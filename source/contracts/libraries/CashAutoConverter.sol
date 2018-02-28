pragma solidity 0.4.20;


import 'trading/ICash.sol';
import 'Controlled.sol';
import 'IAugur.sol';


/**
 * @title Provides modifiers which take care of Cash/ETH conversion
 */
contract CashAutoConverter is Controlled {
    /**
     * @dev Convert any ETH provided in the transaction into Cash before the function executes and convert any remaining Cash balance into ETH after the function completes
     */
    modifier convertToAndFromCash() {
        ethToCash();
        _;
        cashToEth();
    }

    function ethToCash() private returns (bool) {
        if (msg.value > 0) {
            ICash(controller.lookup("Cash")).depositEtherFor.value(msg.value)(msg.sender);
        }
        return true;
    }

    function cashToEth() private returns (bool) {
        ICash _cash = ICash(controller.lookup("Cash"));
        uint256 _tokenBalance = _cash.balanceOf(msg.sender);
        if (_tokenBalance > 0) {
            IAugur augur = controller.getAugur();
            augur.trustedTransfer(_cash, msg.sender, this, _tokenBalance);
            _cash.withdrawEtherTo(msg.sender, _tokenBalance);
        }
        return true;
    }
}
