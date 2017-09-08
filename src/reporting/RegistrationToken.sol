// Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE

pragma solidity ^0.4.13;

import 'ROOT/reporting/IRegistrationToken.sol';
import 'ROOT/libraries/DelegationTarget.sol';
import 'ROOT/libraries/Typed.sol';
import 'ROOT/libraries/Initializable.sol';
import 'ROOT/libraries/token/StandardToken.sol';
import 'ROOT/reporting/IReportingToken.sol';
import 'ROOT/reporting/IBranch.sol';
import 'ROOT/reporting/IReputationToken.sol';
import 'ROOT/reporting/IReportingWindow.sol';
import 'ROOT/reporting/Reporting.sol';


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
        totalSupply += 1;
        if (totalSupply > peakSupply) {
            peakSupply = totalSupply;
        }
        return true;
    }

    function redeem() public returns (bool) {
        require(block.timestamp > reportingWindow.getEndTime());
        require(balances[msg.sender] > 0);
        require(reportingWindow.isDoneReporting(msg.sender));
        balances[msg.sender] -= 1;
        totalSupply -= 1;
        getReputationToken().transfer(msg.sender, Reporting.getRegistrationTokenBondAmount());
        return true;
    }

    function getTypeName() public constant returns (bytes32) {
        return "RegistrationToken";
    }

    function getReportingWindow() public constant returns (IReportingWindow) {
        return reportingWindow;
    }

    function getBranch() public constant returns (IBranch) {
        return reportingWindow.getBranch();
    }

    function getReputationToken() public constant returns (IReputationToken) {
        return reportingWindow.getReputationToken();
    }

    function getPeakSupply() public constant returns (uint256) {
        return peakSupply;
    }
}
