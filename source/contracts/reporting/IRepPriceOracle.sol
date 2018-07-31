pragma solidity 0.4.20;

import 'libraries/Ownable.sol';


contract IRepPriceOracle is Ownable {
    function setRepPriceInAttoEth(uint256 _repPriceInAttoEth) external returns (bool);
    function getRepPriceInAttoEth() external view returns (uint256);
}
