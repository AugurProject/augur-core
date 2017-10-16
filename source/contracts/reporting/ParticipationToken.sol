pragma solidity 0.4.17;


import 'reporting/IParticipationToken.sol';
import 'libraries/DelegationTarget.sol';
import 'libraries/Typed.sol';
import 'libraries/Initializable.sol';
import 'libraries/token/VariableSupplyToken.sol';
import 'reporting/IReputationToken.sol';
import 'reporting/IReportingWindow.sol';
import 'libraries/math/SafeMathUint256.sol';


contract ParticipationToken is DelegationTarget, Typed, Initializable, VariableSupplyToken, IParticipationToken {
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
        require(msg.sender == address(reportingWindow));
        reportingWindow.getReputationToken().trustedTransfer(msg.sender, this, _attotokens);
        mint(msg.sender, _attotokens);
        reportingWindow.increaseTotalWinningStake(_attotokens);
        return true;
    }

    // NOTE: UI should warn users about calling this before first calling `migrateLosingTokens` on all losing tokens with non-dust contents
    // NOTE: we aren't using the convertToAndFromCash modifier here becuase this isn't a whitelisted contract. We expect the reporting window to handle disbursment of ETH
    function redeem(bool forgoFees) public afterInitialized returns (bool) {
        require(reportingWindow.isOver());
        IReputationToken _reputationToken = reportingWindow.getReputationToken();
        uint256 _reputationSupply = _reputationToken.balanceOf(this);
        uint256 _attotokens = balances[msg.sender];
        uint256 _reporterReputationShare = _reputationSupply * _attotokens / supply;
        burn(msg.sender, _attotokens);
        if (_reporterReputationShare != 0) {
            _reputationToken.transfer(msg.sender, _reporterReputationShare);
        }
        reportingWindow.collectReportingFees(msg.sender, _attotokens, forgoFees);
        return true;
    }
}
