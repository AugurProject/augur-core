pragma solidity 0.4.17;
pragma experimental ABIEncoderV2;
pragma experimental "v0.5.0";

import 'libraries/Delegator.sol';
import 'IController.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReputationToken.sol';


contract ReputationTokenFactory {
    function createReputationToken(IController _controller, IUniverse _universe) returns (IReputationToken) {
        Delegator _delegator = new Delegator(_controller, "ReputationToken");
        IReputationToken _reputationToken = IReputationToken(_delegator);
        _reputationToken.initialize(_universe);
        return _reputationToken;
    }
}
