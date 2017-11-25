pragma solidity 0.4.18;

import 'libraries/Delegator.sol';
import 'reporting/IParticipationToken.sol';
import 'reporting/IReportingWindow.sol';
import 'IController.sol';


contract MockParticipationTokenFactory {

    IParticipationToken private participationTokenValue;
    IController private createParticipationTokenControllerValue;
    IReportingWindow private createParticipationTokenReportingWindow;

    function setParticipationTokenValue(IParticipationToken _participationTokenValue) public {
        participationTokenValue = _participationTokenValue;
    }

    function getCreateParticipationTokenControllerValue() public returns(IController) {
        return createParticipationTokenControllerValue;
    }

    function getCreateParticipationTokenReportingWindow() public returns(IReportingWindow) {
        return createParticipationTokenReportingWindow;
    }

    function createParticipationToken(IController _controller, IReportingWindow _reportingWindow) public returns (IParticipationToken) {
        createParticipationTokenControllerValue = _controller;
        createParticipationTokenReportingWindow = _reportingWindow;
        return participationTokenValue;
    }
}
