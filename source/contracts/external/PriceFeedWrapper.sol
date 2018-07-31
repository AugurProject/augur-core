pragma solidity 0.4.20;

import 'libraries/Ownable.sol';
import 'external/MkrPriceFeed/PriceFeed.sol';
import 'external/RepPriceBridge.sol';


contract PriceFeedWrapper is Ownable {
    PriceFeed public priceFeed;
    RepPriceBridge public repPriceBridge;

    function PriceFeedWrapper(PriceFeed _priceFeed, RepPriceBridge _repPriceBridge) public {
        priceFeed = _priceFeed;
        repPriceBridge = _repPriceBridge;
    }

    function post(uint128 val, uint32 zzz, address med) public onlyOwner returns (bool) {
        priceFeed.post(val, zzz, med);
        repPriceBridge.poke();
        return true;
    }

    function setPriceFeed(PriceFeed _priceFeed) public onlyOwner returns (bool) {
        priceFeed = _priceFeed;
        return true;
    }

    function setRepPriceBridge(RepPriceBridge _repPriceBridge) public onlyOwner returns (bool) {
        repPriceBridge = _repPriceBridge;
        return true;
    }

    function onTransferOwnership(address, address) internal returns (bool) {
        return true;
    }
}
