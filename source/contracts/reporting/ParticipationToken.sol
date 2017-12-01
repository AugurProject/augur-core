pragma solidity 0.4.18;


import 'reporting/IParticipationToken.sol';
import 'libraries/DelegationTarget.sol';
import 'libraries/ITyped.sol';
import 'libraries/Initializable.sol';
import 'libraries/token/VariableSupplyToken.sol';
import 'reporting/IReputationToken.sol';
import 'reporting/IReportingWindow.sol';
import 'libraries/Extractable.sol';
import 'libraries/math/SafeMathUint256.sol';


contract ParticipationToken is DelegationTarget, Extractable, ITyped, Initializable, VariableSupplyToken, IParticipationToken {
    using SafeMathUint256 for uint256;

    IReportingWindow private reportingWindow;

    function initialize(IReportingWindow _reportingWindow) public onlyInGoodTimes beforeInitialized returns (bool) {
        endInitialization();
        reportingWindow = _reportingWindow;
        return true;
    }

    // Participation tokens should only be purchasable in the event that every market in a reporting window cannot be reported on
    function buy(uint256 _attotokens) public onlyInGoodTimes afterInitialized returns (bool) {
        require(_attotokens > 0);
        require(reportingWindow.isReportingActive());
        require(reportingWindow.allMarketsFinalized());
        reportingWindow.getReputationToken().trustedParticipationTokenTransfer(msg.sender, this, _attotokens);
        mint(msg.sender, _attotokens);
        reportingWindow.increaseTotalWinningStake(_attotokens);
        return true;
    }

    function redeemForHolder(address _sender, bool forgoFees) public onlyInGoodTimes afterInitialized returns (bool) {
        require(reportingWindow.getUniverse() == IUniverse(msg.sender));
        redeemInternal(_sender, forgoFees);
        return true;
    }

    function redeem(bool forgoFees) public onlyInGoodTimes afterInitialized returns (bool) {
        redeemInternal(msg.sender, forgoFees);
        return true;
    }

    // NOTE: we aren't using the convertToAndFromCash modifier here becuase this isn't a whitelisted contract. We expect the reporting window to handle disbursment of ETH
    function redeemInternal(address _sender, bool forgoFees) private returns (bool) {
        uint256 _attotokens = balances[_sender];
        if (_attotokens != 0) {
            burn(_sender, _attotokens);
            reportingWindow.getReputationToken().transfer(_sender, _attotokens);
        }
        reportingWindow.collectParticipationTokenReportingFees(_sender, _attotokens, forgoFees);
        return true;
    }

    function withdrawInEmergency() public onlyInBadTimes returns (bool) {
        uint256 _attotokens = balances[msg.sender];
        if (_attotokens != 0) {
            burn(msg.sender, _attotokens);
            reportingWindow.getReputationToken().transfer(msg.sender, _attotokens);
        }
        return true;
    }

    function getTypeName() public view returns (bytes32) {
        return "ParticipationToken";
    }

    function getReportingWindow() public view returns (IReportingWindow) {
        return reportingWindow;
    }

    function onTokenTransfer(address _from, address _to, uint256 _value) internal returns (bool) {
        controller.getAugur().logParticipationTokensTransferred(reportingWindow.getUniverse(), _from, _to, _value);
        return true;
    }

    // Disallow REP extraction
    function getProtectedTokens() internal returns (address[] memory) {
        address[] memory _protectedTokens = new address[](1);
        _protectedTokens[0] = reportingWindow.getReputationToken();
        return _protectedTokens;
    }

    function onMint(address _target, uint256 _amount) internal returns (bool) {
        controller.getAugur().logParticipationTokenMinted(reportingWindow.getUniverse(), _target, _amount);
        return true;
    }

    function onBurn(address _target, uint256 _amount) internal returns (bool) {
        controller.getAugur().logParticipationTokenBurned(reportingWindow.getUniverse(), _target, _amount);
        return true;
    }
}
