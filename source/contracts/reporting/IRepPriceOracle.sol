pragma solidity 0.4.18;


contract IRepPriceOracle {
    function setRepPriceInAttoEth(uint256 _repPriceInAttoEth) external returns (uint256);
    function getRepPriceInAttoEth() external view returns (uint256);
}
