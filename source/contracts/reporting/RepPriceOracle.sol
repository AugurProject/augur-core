pragma solidity 0.4.17;

import 'libraries/Ownable.sol';
import 'reporting/IRepPriceOracle.sol';


contract RepPriceOracle is Ownable, IRepPriceOracle {
    
    uint256 private repPriceInAttoEth = 11 * 10 ** 18;
    
    function setRepPriceInAttoEth(uint256 _repPriceInAttoEth) external onlyOwner returns (uint256) {
        repPriceInAttoEth = _repPriceInAttoEth;
    }

    function getRepPriceInAttoEth() external view returns (uint256) {
        return repPriceInAttoEth;
    }
}
