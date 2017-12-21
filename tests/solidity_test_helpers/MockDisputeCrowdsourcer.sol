pragma solidity 0.4.18;

import 'reporting/IDisputeCrowdsourcer.sol';
import 'reporting/IMarket.sol';
import 'TEST/MockVariableSupplyToken.sol';


contract MockDisputeCrowdsourcer is IDisputeCrowdsourcer, MockVariableSupplyToken {
    function initialize(IMarket market, uint256 _size, bytes32 _payoutDistributionHash, uint256[] _payoutNumerators, bool _invalid) public returns (bool) {
        return true;
    }

    function contribute(address _participant, uint256 _amount) public returns (uint256) {
        return 0;
    }
    
    function disavow() public returns (bool) {
        return true;
    }
    
    function getStake() public view returns (uint256) {
        return 0;
    }
    
    function getPayoutDistributionHash() public view returns (bytes32) {
        return bytes32(0);
    }
    
    function liquidateLosing() public returns (bool) {
        return true;
    }
    
    function fork() public returns (bool) {
        return true;
    }
    
    function redeem(address _redeemer) public returns (bool) {
        return true;
    }
    
    function isInvalid() public view returns (bool) {
        return true;
    }
    
    function isDisavowed() public view returns (bool) {
        return true;
    }
    
    function migrate() public returns (bool) {
        return true;
    }
    
    function getPayoutNumerator(uint8 _outcome) public view returns (uint256) {
        return 0;
    }
    
    function getMarket() public view returns (IMarket) {
        return IMarket(0);
    }
    
    function getSize() public view returns (uint256) {
        return 0;
    }
}
