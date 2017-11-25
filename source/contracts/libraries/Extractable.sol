pragma solidity 0.4.18;

/**
 * Contracts inheriting from Extractable can have ETH or ERC20 tokens withdrawn from them by the Controller (if it has "dev mode" enabled).  The allows the Augur team to have the Controller refund ETH or ERC20 tokens that were sent to a contract by mistake.
 */

import 'libraries/token/ERC20Basic.sol';
import 'Controlled.sol';


contract Extractable is Controlled {
    // We use a sentinel value for Ether extraction permission. We're not using ERC20Basic(0) since that can be forbidden inadvertantly by a class providing an incorrectly sized protectedTokens array
    ERC20Basic private constant ETHER_TOKEN = ERC20Basic(1);

    // Send accidentally received ETH to the destination
    function extractEther(address _destination) public onlyControllerCaller returns(bool) {
        require(mayExtract(ETHER_TOKEN));
        require(_destination.call.value(this.balance)());
        return true;
    }

    // Send accidentally received tokens to the destination
    function extractTokens(address _destination, ERC20Basic _token) public onlyControllerCaller returns (bool) {
        require(mayExtract(_token));
        uint256 _balance = _token.balanceOf(this);
        require(_token.transfer(_destination, _balance));
        return true;
    }

    function mayExtract(ERC20Basic _token) private returns (bool) {
        address[] memory _protectedTokens = getProtectedTokens();
        for (uint8 i = 0; i < _protectedTokens.length; i++) {
            if (_protectedTokens[i] == address(_token)) {
                return false;
            }
        }
        return true;
    }

    function getProtectedTokens() internal returns (address[] memory);
}
