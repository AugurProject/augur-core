pragma solidity 0.4.17;

import 'libraries/token/ERC20Basic.sol';
import 'Controlled.sol';


contract Extractable is Controlled {
    // Send accidentally received ETH to the destination
    function extractEther(address _destination) public onlyControllerCaller returns(bool) {
        require(mayExtract(ERC20Basic(0)));
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
