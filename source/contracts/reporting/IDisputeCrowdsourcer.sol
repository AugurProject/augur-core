pragma solidity 0.4.24;

import 'reporting/IReportingParticipant.sol';
import 'reporting/IDisputeWindow.sol';
import 'libraries/token/ERC20.sol';


contract IDisputeCrowdsourcer is IReportingParticipant, ERC20 {
    function initialize(IMarket market, uint256 _size, bytes32 _payoutDistributionHash, uint256[] _payoutNumerators) public returns (bool);
    function contribute(address _participant, uint256 _amount) public returns (uint256);
}
