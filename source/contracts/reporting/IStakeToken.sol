pragma solidity 0.4.17;


import 'libraries/Typed.sol';
import 'libraries/token/ERC20.sol';
import 'reporting/IMarket.sol';


contract IStakeToken is Typed, ERC20 {
    function initialize(IMarket _market, uint256[] _payoutNumerators, bool _invalid) public returns (bool);
    function getMarket() public view returns (IMarket);
    function getPayoutNumerator(uint8 index) public view returns (uint256);
    function getPayoutDistributionHash() public view returns (bytes32);
    function trustedBuy(address _reporter, uint256 _attotokens) public returns (bool);
    function isValid() public view returns (bool);
}
