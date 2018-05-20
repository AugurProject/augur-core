pragma solidity 0.4.20;

import 'reporting/IDisputeCrowdsourcer.sol';
import 'reporting/IMarket.sol';
import 'TEST/MockVariableSupplyToken.sol';


contract MockDisputeCrowdsourcer is IDisputeCrowdsourcer, MockVariableSupplyToken {
    bool private contributeWasCalledValue;
    uint256 private contributeAmountValue;
    address private contributeParticipantValue;
    bytes32 private payoutDistributionHashValue;
    uint256[] private payoutNumeratorsValue;
    uint256 private setSizeValue;

    function initialize(IMarket market, uint256 _size, bytes32 _payoutDistributionHash, uint256[] _payoutNumerators, bool _invalid) public returns (bool) {
        return true;
    }

    function contributeWasCalled() public returns(bool) { return contributeWasCalledValue; }

    function getContributeParticipant() public returns(address) { return contributeParticipantValue; }

    function getContributeAmount() public returns(uint256) { return contributeAmountValue; }

    function contribute(address _participant, uint256 _amount) public returns (uint256) {
        contributeWasCalledValue = true;
        contributeParticipantValue = _participant;
        contributeAmountValue = _amount;
        return 0;
    }

    function disavow() public returns (bool) {
        return true;
    }

    function getStake() public view returns (uint256) {
        return 0;
    }

    function setPayoutNumeratorsValue(uint256[] _payoutNumerators) public {
        payoutNumeratorsValue = _payoutNumerators;
    }

    function setPayoutDistributionHash(bytes32 _hash) public {
        payoutDistributionHashValue = _hash;
    }

    function getPayoutDistributionHash() public view returns (bytes32) {
        return payoutDistributionHashValue;
    }

    function liquidateLosing() public returns (bool) {
        return true;
    }

    function fork() internal returns (bool) {
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

    function getPayoutNumerator(uint256 _outcome) public view returns (uint256) {
        return 0;
    }

    function getMarket() public view returns (IMarket) {
        return IMarket(0);
    }

    function setSize(uint256 _size) public { setSizeValue = _size; }

    function getSize() public view returns (uint256) {
        return setSizeValue;
    }
}
