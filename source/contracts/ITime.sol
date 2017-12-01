pragma solidity 0.4.18;

import 'Controlled.sol';
import 'libraries/Initializable.sol';
import 'libraries/ITyped.sol';
import 'libraries/Extractable.sol';


contract ITime is Controlled, ITyped, Extractable {
    function getTimestamp() external view returns (uint256);

    function getProtectedTokens() internal returns (address[] memory) {
        return new address[](0);
    }
}
