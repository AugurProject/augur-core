pragma solidity 0.4.17;


import 'reporting/IParticipationToken.sol';
import 'libraries/DelegationTarget.sol';
import 'libraries/ITyped.sol';
import 'libraries/Initializable.sol';
import 'libraries/token/VariableSupplyToken.sol';
import 'reporting/IReputationToken.sol';
import 'reporting/IReportingWindow.sol';
import 'libraries/math/SafeMathUint256.sol';


contract ParticipationToken is DelegationTarget, ITyped, Initializable, VariableSupplyToken, IParticipationToken {
    using SafeMathUint256 for uint256;

    IReportingWindow private reportingWindow;

    function initialize(IReportingWindow _reportingWindow) public onlyInGoodTimes beforeInitialized returns (bool) {
        endInitialization();
        reportingWindow = _reportingWindow;
        return true;
    }

    function buy(uint256 _attotokens) public onlyInGoodTimes afterInitialized returns (bool) {
        require(_attotokens > 0);
        require(reportingWindow.isReportingActive());
        require(reportingWindow.allMarketsFinalized());
        reportingWindow.getReputationToken().trustedParticipationTokenTransfer(msg.sender, this, _attotokens);
        mint(msg.sender, _attotokens);
        reportingWindow.increaseTotalWinningStake(_attotokens);
        return true;
    }

    // NOTE: we aren't using the convertToAndFromCash modifier here becuase this isn't a whitelisted contract. We expect the reporting window to handle disbursment of ETH
    function redeem(bool forgoFees) public onlyInGoodTimes afterInitialized returns (bool) {
        uint256 _attotokens = balances[msg.sender];
        if (_attotokens != 0) {
            burn(msg.sender, _attotokens);
            reportingWindow.getReputationToken().transfer(msg.sender, _attotokens);
        }
        reportingWindow.collectParticipationTokenReportingFees(msg.sender, _attotokens, forgoFees);
        return true;
    }

    function getTypeName() public view returns (bytes32) {
        return "ParticipationToken";
    }

    function getReportingWindow() public view returns (IReportingWindow) {
        return reportingWindow;
    }

    function emitCustomTransferLogs(address _from, address _to, uint256 _value) internal returns (bool) {
        controller.getAugur().logParticipationTokensTransferred(reportingWindow.getUniverse(), _from, _to, _value);
        return true;
    }
}
