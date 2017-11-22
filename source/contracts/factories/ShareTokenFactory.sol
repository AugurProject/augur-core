pragma solidity 0.4.18;


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
