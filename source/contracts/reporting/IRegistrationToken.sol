pragma solidity 0.4.18;


import 'libraries/ITyped.sol';
import 'libraries/token/ERC20.sol';
import 'reporting/IReportingWindow.sol';


contract IRegistrationToken is ITyped, ERC20 {
    function initialize(IReportingWindow _reportingWindow) public returns (bool);
    function getReportingWindow() public view returns (IReportingWindow);
    function getPeakSupply() public view returns (uint256);
}
