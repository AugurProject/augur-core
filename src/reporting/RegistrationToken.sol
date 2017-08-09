// Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE

pragma solidity ^0.4.13;

import 'ROOT/libraries/DelegationTarget.sol';
import 'ROOT/libraries/Typed.sol';
import 'ROOT/libraries/Initializable.sol';
import 'ROOT/libraries/token/StandardToken.sol';
import 'ROOT/reporting/ReportingToken.sol';
import 'ROOT/reporting/Branch.sol';
import 'ROOT/reporting/ReputationToken.sol';
import 'ROOT/reporting/Interfaces.sol';


contract RegistrationToken is DelegationTarget, Typed, Initializable, StandardToken {
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
        // 10 ** 18 is the Bond Amount
        getReputationToken().trustedTransfer(msg.sender, this, 10 ** 18);
        balances[msg.sender] += 1;
        totalSupply += 1;
        if (totalSupply > peakSupply) {
            peakSupply = totalSupply;
        }
        return true;
    }

    // FIXME: currently, if a market is disputed it is removed from the set of markets that need reporting. This can lead to being unable to redeem registration tokens because there the function for calculating markets to be reported on may end up dividing by zero (especially during a fork when all markets migrate away from the reporting window).  it also generally messes with the math of how many reports a user needs to do since the result is calculated dynamically based on current state, not based on the state when reports were made
    function redeem() public returns (bool) {
        require(block.timestamp > reportingWindow.getEndTime());
        require(balances[msg.sender] > 0);
        require(reportingWindow.isDoneReporting(msg.sender));
        balances[msg.sender] -= 1;
        totalSupply -= 1;
        // 10 ** 18 is the Bond Amount
        getReputationToken().transfer(msg.sender, 10 ** 18);
        return true;
    }

    function getTypeName() public constant returns (bytes32) { 
        return "RegistrationToken";
    }

    function getReportingWindow() public constant returns (IReportingWindow) {
        return reportingWindow;
    }

    function getBranch() public constant returns (Branch) {
        return reportingWindow.getBranch();
    }

    function getReputationToken() public constant returns (ReputationToken) {
        return reportingWindow.getReputationToken();
    }

    function getPeakSupply() public constant returns (uint256) {
        return peakSupply;
    }
}
