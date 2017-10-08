pragma solidity 0.4.17;
pragma experimental ABIEncoderV2;
pragma experimental "v0.5.0";

import 'libraries/Delegator.sol';
import 'reporting/IMarket.sol';
import 'IController.sol';



contract ShareTokenFactory {
    function createShareToken(IController _controller, IMarket _market, uint8 _outcome) public returns (IShareToken) {
        Delegator _delegator = new Delegator(_controller, "ShareToken");
        IShareToken _shareToken = IShareToken(_delegator);
        _shareToken.initialize(_market, _outcome);
        return _shareToken;
    }
}
