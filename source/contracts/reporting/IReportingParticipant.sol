pragma solidity 0.4.18;

import 'reporting/IMarket.sol';
import 'reporting/IFeeWindow.sol';


contract IReportingParticipant {
    function getStake() public view returns (uint256);
    function getPayoutDistributionHash() public view returns (bytes32);
    function liquidateLosing() public returns (bool);
    function fork() public returns (bool);
    function redeem(address _redeemer) public returns (bool);
    function isInvalid() public view returns (bool);
    function isDisavowed() public view returns (bool);
    function migrate() public returns (bool);
    function getPayoutNumerator(uint8 _outcome) public view returns (uint256);
    function getMarket() public view returns (IMarket);
    function getSize() public view returns (uint256);
}
