pragma solidity ^0.4.13;

import 'ROOT/libraries/Typed.sol';
import 'ROOT/libraries/token/ERC20.sol';
import 'ROOT/reporting/IReportingWindow.sol';


contract IRegistrationToken is Typed, ERC20 {
    function initialize(IReportingWindow _reportingWindow) public returns (bool);
    function getReportingWindow() public constant returns (IReportingWindow);
    function getPeakSupply() public constant returns (uint256);
}
