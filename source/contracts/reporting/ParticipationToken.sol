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

    function initialize(IReportingWindow _reportingWindow) public beforeInitialized returns (bool) {
        endInitialization();
        reportingWindow = _reportingWindow;
        return true;
    }

    function buy(uint256 _attotokens) public afterInitialized returns (bool) {
        require(_attotokens > 0);
        require(reportingWindow.isReportingActive());
        require(reportingWindow.allMarketsFinalized());
        reportingWindow.getReputationToken().trustedReportingAttendanceTokenTransfer(msg.sender, this, _attotokens);
        mint(msg.sender, _attotokens);
        reportingWindow.increaseTotalWinningStake(_attotokens);
        return true;
    }

    // NOTE: we aren't using the convertToAndFromCash modifier here becuase this isn't a whitelisted contract. We expect the reporting window to handle disbursment of ETH
    function redeem(bool forgoFees) public afterInitialized returns (bool) {
        uint256 _attotokens = balances[msg.sender];
        if (_attotokens != 0) {
            burn(msg.sender, _attotokens);
            reportingWindow.getReputationToken().transfer(msg.sender, _attotokens);
        }
        reportingWindow.collectAttedanceTokenReportingFees(msg.sender, _attotokens, forgoFees);
        return true;
    }

    function getTypeName() public view returns (bytes32) {
        return "ParticipationToken";
    }

    function getReportingWindow() public view returns (IReportingWindow) {
        return reportingWindow;
    }
}
