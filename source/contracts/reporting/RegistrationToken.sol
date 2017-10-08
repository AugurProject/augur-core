// Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE

pragma solidity 0.4.17;
pragma experimental ABIEncoderV2;
pragma experimental "v0.5.0";

import 'reporting/IRegistrationToken.sol';
import 'libraries/DelegationTarget.sol';
import 'libraries/Typed.sol';
import 'libraries/Initializable.sol';
import 'libraries/token/StandardToken.sol';
import 'reporting/IReportingToken.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReputationToken.sol';
import 'reporting/IReportingWindow.sol';
import 'reporting/Reporting.sol';


contract RegistrationToken is DelegationTarget, Typed, Initializable, StandardToken, IRegistrationToken {
    IReportingWindow private reportingWindow;
    uint256 private peakSupply;

    function initialize(IReportingWindow _reportingWindow) public beforeInitialized returns (bool) {
        endInitialization();
        reportingWindow = _reportingWindow;
        return true;
    }

    function register() public returns (bool) {
        // do not allow for registration for reporting in the current window or past windows
        require(block.timestamp < reportingWindow.getStartTime());
        require(balances[msg.sender] == 0);
        getReputationToken().trustedTransfer(msg.sender, this, Reporting.getRegistrationTokenBondAmount());
        balances[msg.sender] += 1;
        supply += 1;
        if (supply > peakSupply) {
            peakSupply = supply;
        }
        return true;
    }

    function redeem() public returns (bool) {
        require(block.timestamp > reportingWindow.getEndTime());
        require(balances[msg.sender] > 0);
        require(reportingWindow.isDoneReporting(msg.sender));
        balances[msg.sender] -= 1;
        supply -= 1;
        getReputationToken().transfer(msg.sender, Reporting.getRegistrationTokenBondAmount());
        return true;
    }

    function getTypeName() public constant returns (bytes32) {
        return "RegistrationToken";
    }

    function getReportingWindow() public constant returns (IReportingWindow) {
        return reportingWindow;
    }

    function getUniverse() public constant returns (IUniverse) {
        return reportingWindow.getUniverse();
    }

    function getReputationToken() public constant returns (IReputationToken) {
        return reportingWindow.getReputationToken();
    }

    function getPeakSupply() public constant returns (uint256) {
        return peakSupply;
    }
}
