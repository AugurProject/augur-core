pragma solidity 0.4.20;

import 'reporting/IFeeToken.sol';
import 'reporting/IFeeWindow.sol';
import 'libraries/DelegationTarget.sol';
import 'TEST/MockVariableSupplyToken.sol';


contract MockFeeToken is DelegationTarget, MockVariableSupplyToken, IFeeToken {
    bool private onBurnCalledValue;
    bool private onMintCalledValue;
    bool private onTokenTransferValue;
    IFeeWindow private initializeFeeWindowValue;
    address private feeWindowBurnTargetValue;
    uint256 private feeWindowBurnAmountValue;
    address private mintForReportingParticipantTargetValue;
    uint256 private mintForReportingParticipantAmountValue;
    address private onTokenTransferFromValue;
    address private onTokenTransferToValue;
    uint256 private onTokenTransferValueValue;
    address private onMintTargetValue;
    uint256 private onMintAmountValue;
    address private onBurnTargetValue;
    uint256 private onBurnAmountValue;

    function reset() public {
        onBurnCalledValue = false;
        onMintCalledValue = false;
        onTokenTransferValue = false;
        feeWindowBurnTargetValue = address(0);
        feeWindowBurnAmountValue = 0;
    }

    function onBurnCalled() public returns(bool) {
        return onBurnCalledValue;
    }

    function onMintCalled() public returns(bool) {
        return onMintCalledValue;
    }

    function onTokenTransferCalled() public returns(bool) {
        return onTokenTransferValue;
    }

    function getInitializedFeeWindow() public returns(IFeeWindow) {
        return initializeFeeWindowValue;
    }

    function initialize(IFeeWindow _feeWindow) public beforeInitialized returns (bool) {
        initializeFeeWindowValue = _feeWindow;
        return true;
    }

    function getFeeWindow() public view returns (IFeeWindow) {
        return initializeFeeWindowValue;
    }

    function getFeeWindowBurnTargetValue() public returns(address) { return feeWindowBurnTargetValue; }

    function getFeeWindowBurnAmountValue() public returns(uint256) { return feeWindowBurnAmountValue; }

    function feeWindowBurn(address _target, uint256 _amount) public returns (bool) {
        feeWindowBurnTargetValue = _target;
        feeWindowBurnAmountValue = _amount;
        return true;
    }

    function getMintForReportingParticipantTargetValue() public returns(address) { return mintForReportingParticipantTargetValue; }

    function getMintForReportingParticipantAmountValue() public returns(uint256) { return mintForReportingParticipantAmountValue; }

    function mintForReportingParticipant(address _target, uint256 _amount) public returns (bool) {
        mintForReportingParticipantTargetValue = _target;
        mintForReportingParticipantAmountValue = _amount;
        return true;
    }

    function getOnTokenTransferFromValue() public returns (address) { return onTokenTransferFromValue;}

    function getOnTokenTransferToValue() public returns (address) { return onTokenTransferToValue;}

    function getOnTokenTransferValueValue() public returns (uint256) { return onTokenTransferValueValue;}

    function getOnMintTargetValue() public returns (address) { return onMintTargetValue;}

    function getOnMintAmountValue() public returns (uint256) { return onMintAmountValue;}

    function getOnBurnTargetValue() public returns (address) { return onBurnTargetValue;}

    function getOnBurnAmountValue() public returns (uint256) { return onBurnAmountValue;}

    function onBurn(address _target, uint256 _amount) internal returns (bool) {
        onBurnCalledValue = true;
        onBurnTargetValue = _target;
        onBurnAmountValue = _amount;
        return true;
    }

    function onTokenTransfer(address _from, address _to, uint256 _value) internal returns (bool) {
        onTokenTransferValue = true;
        onTokenTransferFromValue = _from;
        onTokenTransferToValue = _to;
        onTokenTransferValueValue = _value;
        return true;
    }

    function onMint(address _target, uint256 _amount) internal returns (bool) {
        onMintCalledValue = true;
        onMintTargetValue = _target;
        onMintAmountValue = _amount;
        return true;
    }
}