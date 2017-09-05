pragma solidity ^0.4.13;

import 'ROOT/reporting/IMarket.sol';


contract ICompleteSets {
    function publicBuy(address _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupID) external returns (bytes32);
    function publicSell(address _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupID) external returns (bytes32);
    function publicTrade(uint8 _direction, address _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupID) external returns (bytes32);
    function publicTakeBestOrder(uint8 _direction, address _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupID) external returns (uint256);
    function trade(address _sender, uint8 _direction, address _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupID) internal returns (bytes32);
    function takeBestOrder(address _sender, uint8 _direction, address _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupID) internal returns (uint256);
}
