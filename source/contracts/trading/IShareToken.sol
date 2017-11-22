pragma solidity 0.4.18;


import 'libraries/ITyped.sol';
import 'libraries/token/ERC20.sol';
import 'reporting/IMarket.sol';


contract IShareToken is ITyped, ERC20 {
    function initialize(IMarket _market, uint8 _outcome) external returns (bool);
    function createShares(address _owner, uint256 _amount) external returns (bool);
    function destroyShares(address, uint256 balance) external returns (bool);
    function getMarket() external view returns (IMarket);
    function getOutcome() external view returns (uint8);
    function trustedOrderTransfer(address _source, address _destination, uint256 _attotokens) public returns (bool);
    function trustedFillOrderTransfer(address _source, address _destination, uint256 _attotokens) public returns (bool);
}
