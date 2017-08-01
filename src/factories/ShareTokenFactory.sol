pragma solidity ^0.4.13;

import 'ROOT/libraries/Delegator.sol';
import 'ROOT/Controller.sol';


// FIXME: remove once this can be imported as a solidty contract
contract Market {
    function stub() {}
}


// FIXME: remove once this can be imported as a solidty contract
contract ShareToken {
    function initialize(Market _market, int256 _outcome);
}


contract ShareTokenFactory {
    function createShareToken(Controller _controller, Market _market, int256 _outcome) returns (ShareToken) {
        Delegator _delegator = new Delegator(_controller, "shareToken");
        ShareToken _shareToken = ShareToken(_delegator);
        _shareToken.initialize(_market, _outcome);
        return _shareToken;
    }
}