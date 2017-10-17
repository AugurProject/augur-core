pragma solidity 0.4.17;


import 'libraries/Delegator.sol';
import 'reporting/IWindowParticipationToken.sol';
import 'reporting/IReportingWindow.sol';
import 'IController.sol';


contract WindowParticipationTokenFactory {
    function createWindowParticipationToken(IController _controller, IReportingWindow _reportingWindow) public returns (IWindowParticipationToken) {
        Delegator _delegator = new Delegator(_controller, "WindowParticipationToken");
        IWindowParticipationToken _participationToken = IWindowParticipationToken(_delegator);
        _participationToken.initialize(_reportingWindow);
        return _participationToken;
    }
}
