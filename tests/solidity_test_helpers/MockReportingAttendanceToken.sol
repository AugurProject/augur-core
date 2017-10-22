pragma solidity 0.4.17;


import 'reporting/IReportingAttendanceToken.sol';
import 'libraries/DelegationTarget.sol';
import 'libraries/ITyped.sol';
import 'libraries/Initializable.sol';
import 'libraries/token/VariableSupplyToken.sol';
import 'reporting/IReputationToken.sol';
import 'reporting/IReportingWindow.sol';
import 'libraries/math/SafeMathUint256.sol';


contract MockReportingAttendanceToken is ITyped, Initializable, VariableSupplyToken, IReportingAttendanceToken {
    using SafeMathUint256 for uint256;

    IReportingWindow private initializeReportingWindowValue;
    IReportingWindow private setReportingWindowValue;
    uint256 private buyValue;
    bool private redeemForgoFeesValue;

    function getInitializeReportingWindow() public returns (IReportingWindow) {
        return initializeReportingWindowValue;
    }

    function setReportingWindow(IReportingWindow _reportingWindow) public {
        setReportingWindowValue = _reportingWindow;
    }

    function getBuyValue() public returns(uint256) {
        return buyValue;
    }

    function getRedeemForgoFeesValue() public returns(bool) {
        return redeemForgoFeesValue;
    }
    
    function buy(uint256 _attotokens) public afterInitialized returns (bool) {
        buyValue = _attotokens;
        return true;
    }

    function redeem(bool forgoFees) public afterInitialized returns (bool) {
        redeemForgoFeesValue = forgoFees;
        return true;
    }

    function initialize(IReportingWindow _reportingWindow) public returns (bool) {
        endInitialization();
        initializeReportingWindowValue = _reportingWindow;
        return true;
    }

    function getReportingWindow() public view returns (IReportingWindow) {
        return setReportingWindowValue;
    }

    function getTypeName() public view returns (bytes32) {
        return "ReportingAttendanceToken";
    }

}