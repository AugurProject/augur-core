pragma solidity 0.4.20;

import 'libraries/Ownable.sol';
import 'reporting/IRepPriceOracle.sol';
import 'external/MkrPriceFeed/Medianizer.sol';


contract RepPriceBridge is Ownable {
    IRepPriceOracle public repPriceOracle;
    Medianizer public medianizer;

    function RepPriceBridge(IRepPriceOracle _repPriceOracle, Medianizer _medianizer) public {
        repPriceOracle = _repPriceOracle;
        medianizer = _medianizer;
    }

    function poke() public returns (bool) {
        bytes32 price;
        bool isValid;
        (price, isValid) = medianizer.peek();
        if (isValid) {
            repPriceOracle.setRepPriceInAttoEth(uint256(price));
        }
        return isValid;
    }

    function setRepPriceOracle(IRepPriceOracle _repPriceOracle) public onlyOwner returns (bool) {
        repPriceOracle = _repPriceOracle;
        return true;
    }

    function setMedianizer(Medianizer _medianizer) public onlyOwner returns (bool) {
        medianizer = _medianizer;
        return true;
    }

    function transferRepPriceOracleOwnership(address _newOwner) public onlyOwner returns (bool) {
        repPriceOracle.transferOwnership(_newOwner);
        return true;
    }

    function onTransferOwnership(address, address) internal returns (bool) {
        return true;
    }
}
