pragma solidity 0.4.24;


import 'libraries/CloneFactory.sol';
import 'reporting/IMarket.sol';
import 'IController.sol';
import 'IControlled.sol';


contract ShareTokenFactory is CloneFactory {
    function createShareToken(IController _controller, IMarket _market, uint256 _outcome) public returns (IShareToken) {
        IShareToken _shareToken = IShareToken(createClone(_controller.lookup("ShareToken")));
        IControlled(_shareToken).setController(_controller);
        _shareToken.initialize(_market, _outcome);
        return _shareToken;
    }
}
