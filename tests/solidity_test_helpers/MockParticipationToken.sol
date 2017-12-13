pragma solidity 0.4.18;


import 'reporting/IFeeWindow.sol';
import 'libraries/DelegationTarget.sol';
import 'libraries/ITyped.sol';
import 'libraries/Initializable.sol';
import 'reporting/IReputationToken.sol';
import 'reporting/IFeeWindow.sol';
import 'libraries/math/SafeMathUint256.sol';
import 'TEST/MockVariableSupplyToken.sol';


contract MockFeeWindow is ITyped, Initializable, MockVariableSupplyToken, IFeeWindow {
    using SafeMathUint256 for uint256;

    IFeeWindow private initializeFeeWindowValue;
    IFeeWindow private setFeeWindowValue;
    uint256 private buyValue;
    bool private redeemForgoFeesValue;

    function getInitializeFeeWindow() public returns (IFeeWindow) {
        return initializeFeeWindowValue;
    }

    function setFeeWindow(IFeeWindow _feeWindow) public {
        setFeeWindowValue = _feeWindow;
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

    function callIncreaseTotalWinningStake(IFeeWindow _feeWindow, uint256 _attotokens) public returns (bool) {
        return _feeWindow.increaseTotalWinningStake(_attotokens);
    }

    function callCollectFeeWindowReportingFees(IFeeWindow _feeWindow, address _reporterAddress, uint256 _attoStake, bool _forgoFees) public returns(uint256) {
        return _feeWindow.collectFeeWindowReportingFees(_reporterAddress, _attoStake, _forgoFees);
    }

    function callTrustedFeeWindowTransfer(IReputationToken _reputationToken, address _source, address _destination, uint256 _attotokens) public returns (bool) {
        return _reputationToken.trustedFeeWindowTransfer(_source, _destination, _attotokens);
    }

    function getTypeName() public view returns (bytes32) {
        return "FeeWindow";
    }

    function initialize(IFeeWindow _feeWindow) public returns (bool) {
        endInitialization();
        initializeFeeWindowValue = _feeWindow;
        return true;
    }

    function getFeeWindow() public view returns (IFeeWindow) {
        return setFeeWindowValue;
    }

    function redeemForHolder(address _sender, bool forgoFees) public returns (bool) {
        return true;
    }
}
