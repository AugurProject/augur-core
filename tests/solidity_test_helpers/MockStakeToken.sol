pragma solidity 0.4.17;


import 'reporting/IStakeToken.sol';
import 'libraries/ITyped.sol';
import 'libraries/Initializable.sol';
import 'reporting/IUniverse.sol';
import 'reporting/IReputationToken.sol';
import 'reporting/IStakeToken.sol';
import 'reporting/IDisputeBond.sol';
import 'reporting/IReportingWindow.sol';
import 'reporting/IMarket.sol';
import 'libraries/math/SafeMathUint256.sol';
import 'TEST/MockVariableSupplyToken.sol';


contract MockStakeToken is ITyped, MockVariableSupplyToken, IStakeToken {
    using SafeMathUint256 for uint256;

    IMarket private initializeMarketValue;
    uint256[] private initializePayoutNumeratorsValue;
    bool private initializeInvalidValue;
    IMarket private setMarketValue;
    uint256 private setPayoutNumeratorValue;
    bytes32 private setPayoutDeistributionHashValue;
    address private trustedBuyAddressValue;
    uint256 private trustedBuyAttoTokensValue;
    bool private setIsValidValue;

    function getInitializeMarketValue() public returns(IMarket) {
        return initializeMarketValue;
    }
    
    function getInitializePayoutNumeratorsValue() public returns(uint256[]) {
        return initializePayoutNumeratorsValue;
    }

    function getInitializeInvalidValue() public returns(bool) {
        return initializeInvalidValue;
    }

    function setMarket(IMarket _setMarketValue) public {
        setMarketValue = _setMarketValue;
    }

    function setPayoutNumerator(uint256 _setPayoutNumeratorValue) public {
        setPayoutNumeratorValue = _setPayoutNumeratorValue;
    }

    function setPayoutDistributionHash(bytes32 _setPayoutDeistributionHashValue) public {
        setPayoutDeistributionHashValue = _setPayoutDeistributionHashValue;
    }

    function getTrustedBuyAddressValue() public returns(address) {
        return trustedBuyAddressValue;
    }

    function getTrustedBuyAttoTokensValue() public returns(uint256) {
        return trustedBuyAttoTokensValue;
    }

    function setIsValid(bool _setIsValidValue) public {
        setIsValidValue = _setIsValidValue;
    }

    function getTypeName() public view returns (bytes32) {
        return "StakeToken";
    }

    function callNoteReportingGasPrice(IMarket _market, IReportingWindow _reportingWindow) public returns (bool) {
        return _reportingWindow.noteReportingGasPrice(_market);
    }

    function callCollectReportingFees(address _reporterAddress, uint256 _attoStake, bool _forgoFees, IReportingWindow _reportingWindow) public returns(uint256) {
        return _reportingWindow.collectStakeTokenReportingFees(_reporterAddress, _attoStake, _forgoFees);
    }

    function callMigrateOutStakeToken(IReputationToken _reputationToken, IReputationToken  _destination, address _reporter, uint256 _attotokens) public returns(bool) {
        return _reputationToken.migrateOutStakeToken(_destination, _reporter, _attotokens);
    }

    function callMigrateOut(IReputationToken _reputationToken, IReputationToken  _destination, address _reporter, uint256 _attotokens) public returns(bool) {
        return _reputationToken.migrateOut(_destination, _reporter, _attotokens);
    }

    function initialize(IMarket _market, uint256[] _payoutNumerators, bool _invalid) public returns (bool) {
        initializeMarketValue = _market;
        initializePayoutNumeratorsValue = _payoutNumerators;
        initializeInvalidValue = _invalid;
        return true;
    }

    function getMarket() public view returns (IMarket) {
        return setMarketValue;
    }

    function getPayoutNumerator(uint8 index) public view returns (uint256) {
        return setPayoutNumeratorValue;
    }

    function getPayoutDistributionHash() public view returns (bytes32) {
        return setPayoutDeistributionHashValue;
    }

    function trustedBuy(address _reporter, uint256 _attotokens) public returns (bool) {
        trustedBuyAddressValue = _reporter;
        trustedBuyAttoTokensValue = _attotokens;
    }

    function isValid() public view returns (bool) {
        return setIsValidValue;
    }
}
