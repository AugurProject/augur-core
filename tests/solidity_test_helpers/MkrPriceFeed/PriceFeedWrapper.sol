pragma solidity 0.4.20;

import 'libraries/Ownable.sol';
import 'TEST/MkrPriceFeed/PriceFeed.sol';
import 'TEST/MkrPriceFeed/RepPriceBridge.sol';


contract PriceFeedWrapper is Ownable {
    PriceFeed public priceFeed;
    RepPriceBridge public repPriceBridge;

    function PriceFeedWrapper(PriceFeed _priceFreed, RepPriceBridge _repPriceBridge) public {
        priceFeed = _priceFeed;
        repPriceBridge = _repPriceBridge;
    }

    function post(uint128 val, uint32 zzz, address med) public onlyOwner returns (bool) {
        priceFeed.post(val, zzz, med);
        repPriceBridge.poke();
        return true;
    }

    function setRepPriceBridge(address _repPriceBridge) public onlyOwner returns (bool) {
        repPriceBridge = _repPriceBridge;
        return true;
    }

    function transferPriceFeedOwnership(address _newOwner) public onlyOwner returns (bool) {
        priceFeed.transferOwnership(_newOwner);
        return true;
    }
}