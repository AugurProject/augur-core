pragma solidity 0.4.18;


import 'libraries/ITyped.sol';
import 'libraries/token/ERC20.sol';
import 'reporting/IMarket.sol';


contract IStakeToken is ITyped, ERC20 {
    function initialize(IMarket _market, uint256[] _payoutNumerators, bool _invalid) public returns (bool);
    function getMarket() public view returns (IMarket);
    function getPayoutNumerator(uint8 index) public view returns (uint256);
    function getPayoutDistributionHash() public view returns (bytes32);
    function trustedBuy(address _reporter, uint256 _attotokens) public returns (bool);
    function isValid() public view returns (bool);
    function redeemDisavowedTokens(address _reporter) public returns (bool);
    function redeemWinningTokensForHolder(address _sender, bool forgoFees) public returns (bool);
    function redeemForkedTokensForHolder(address _sender) public returns (bool);
    function isDisavowed() public view returns (bool);
    function isForked() public view returns (bool);
}
