pragma solidity 0.4.17;


import 'libraries/Typed.sol';
import 'libraries/token/ERC20.sol';
import 'reporting/IReportingWindow.sol';


contract IRegistrationToken is Typed, ERC20 {
    function initialize(IReportingWindow _reportingWindow) public returns (bool);
    function getReportingWindow() public view returns (IReportingWindow);
    function getPeakSupply() public view returns (uint256);
}
