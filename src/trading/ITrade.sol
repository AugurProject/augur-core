pragma solidity ^0.4.13;

import 'ROOT/reporting/IMarket.sol';
import 'ROOT/trading/Trading.sol';


contract ITrade {
    function publicBuy(IMarket _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupID) external returns (bytes32);
    function publicSell(IMarket _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupID) external returns (bytes32);
    function publicTrade(Trading.TradeDirections _direction, IMarket _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupID) external returns (bytes32);
    function publicTakeBestOrder(Trading.TradeDirections _direction, IMarket _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupID) external returns (uint256);
    function trade(address _sender, Trading.TradeDirections _direction, IMarket _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupID) internal returns (bytes32);
    function takeBestOrder(address _sender, Trading.TradeDirections _direction, IMarket _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupID) internal returns (uint256);
}
