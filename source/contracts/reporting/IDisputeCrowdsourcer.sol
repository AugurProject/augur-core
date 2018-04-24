pragma solidity 0.4.20;

import 'reporting/IReportingParticipant.sol';
import 'reporting/IFeeWindow.sol';
import 'libraries/token/ERC20.sol';


contract IDisputeCrowdsourcer is IReportingParticipant, ERC20 {
    function initialize(IMarket market, uint256 _size, bytes32 _payoutDistributionHash, uint256[] _payoutNumerators, bool _invalid) public returns (bool);
    function contribute(address _participant, uint256 _amount) public returns (uint256);
}
