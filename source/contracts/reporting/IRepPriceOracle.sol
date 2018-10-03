pragma solidity 0.4.24;


contract IRepPriceOracle {
    function setRepPriceInAttoEth(uint256 _repPriceInAttoEth) external returns (bool);
    function getRepPriceInAttoEth() public view returns (uint256);
}
