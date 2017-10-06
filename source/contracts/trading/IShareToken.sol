pragma solidity ^0.4.17;

import 'libraries/Typed.sol';
import 'libraries/token/ERC20.sol';
import 'reporting/IMarket.sol';


contract IShareToken is Typed, ERC20 {
    function initialize(IMarket _market, uint8 _outcome) external returns (bool);
    function createShares(address _owner, uint256 _amount) external returns (bool);
    function destroyShares(address, uint256 balance) external returns (bool);
    function getMarket() external constant returns (IMarket);
    function getOutcome() external constant returns (uint8);
}
