pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/reporting/Market.sol';
import 'ROOT/reporting/Interfaces.sol';
import 'ROOT/Controller.sol';



contract ShareTokenFactory {
    function createShareToken(Controller _controller, Market _market, uint8 _outcome) public returns (IShareToken) {
        Delegator _delegator = new Delegator(_controller, "shareToken");
        IShareToken _shareToken = IShareToken(_delegator);
        _shareToken.initialize(_market, _outcome);
        return _shareToken;
    }
}