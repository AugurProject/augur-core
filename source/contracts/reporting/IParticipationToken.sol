pragma solidity 0.4.18;

import 'libraries/token/ERC20.sol';
import 'reporting/IReportingWindow.sol';


contract IParticipationToken is ERC20 {
    function initialize(IReportingWindow _reportingWindow) public returns (bool);
    function getReportingWindow() public view returns (IReportingWindow);
    function redeemForHolder(address _sender, bool forgoFees) public returns (bool);
}
