pragma solidity 0.4.17;


import 'libraries/Delegator.sol';
import 'reporting/IParticipationToken.sol';
import 'reporting/IReportingWindow.sol';
import 'IController.sol';


contract ParticipationTokenFactory {
    function createParticipationToken(IController _controller, IReportingWindow _reportingWindow) public returns (IParticipationToken) {
        Delegator _delegator = new Delegator(_controller, "ParticipationToken");
        IParticipationToken _participationToken = IParticipationToken(_delegator);
        _participationToken.initialize(_reportingWindow);
        return _participationToken;
    }
}
