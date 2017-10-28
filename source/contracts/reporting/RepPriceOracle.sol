pragma solidity 0.4.17;

import 'libraries/Ownable.sol';
import 'reporting/IRepPriceOracle.sol';


contract RepPriceOracle is Ownable, IRepPriceOracle {

    // A rough initial estimate based on the current date (10/26/2017) 1 REP ~= .06 ETH
    uint256 private repPriceInAttoEth = 6 * 10 ** 16;

    function setRepPriceInAttoEth(uint256 _repPriceInAttoEth) external onlyOwner returns (uint256) {
        repPriceInAttoEth = _repPriceInAttoEth;
    }

    function getRepPriceInAttoEth() external view returns (uint256) {
        return repPriceInAttoEth;
    }
}
