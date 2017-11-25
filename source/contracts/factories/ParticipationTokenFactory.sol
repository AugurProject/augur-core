pragma solidity 0.4.18;


import 'libraries/Delegator.sol';
import 'reporting/IParticipationToken.sol';
import 'reporting/IReportingWindow.sol';
import 'IController.sol';


contract ParticipationTokenFactory {
    function createParticipationToken(IController _controller, IReportingWindow _reportingWindow) public returns (IParticipationToken) {
        Delegator _delegator = new Delegator(_controller, "ParticipationToken");
        IParticipationToken _token = IParticipationToken(_delegator);
        _token.initialize(_reportingWindow);
        return _token;
    }
}
