pragma solidity 0.4.24;


import 'IController.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReputationToken.sol';


contract MockReputationTokenFactory {
    IUniverse private createReputationTokenUniverseValue;
    IReputationToken private createReputationTokenValue;

    function getCreateReputationTokenUniverse() public returns(IUniverse) {
        return createReputationTokenUniverseValue;
    }

    function setCreateReputationTokenValue(IReputationToken _reputationTokenValue) public {
        createReputationTokenValue = _reputationTokenValue;
    }

    function createReputationToken(IController _controller, IUniverse _universe, IUniverse _parentUniverse) public returns (IReputationToken) {
        createReputationTokenUniverseValue = _universe;
        return createReputationTokenValue;
    }
}
