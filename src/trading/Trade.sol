// Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE

import 'ROOT/trading/ICompleteSets.sol';
import 'ROOT/Controlled.sol';
import 'ROOT/libraries/ReentrancyGuard.sol';
import 'ROOT/libraries/math/SafeMathUint256.sol';
import 'ROOT/libraries/token/ERC20.sol';
import 'ROOT/extensions/MarketFeeCalculator.sol';
import 'ROOT/reporting/IMarket.sol';
import 'ROOT/reporting/IReportingWindow.sol';
import 'ROOT/trading/IOrders.sol';

macro ORDERS: controller.lookup('Orders')
macro TAKEORDER: controller.lookup('takeOrder')
macro MAKEORDER: controller.lookup('makeOrder')

contract Trade is Controlled, Typed {

    uint8 private constant BID = 1;
    uint8 private constant ASK = 2;
    uint8 private constant BUYING = 1;
    uint8 private constant SELLING = 2;
    uint256 private constant MINIMUM_GAS_NEEDED = 300000

    function publicBuy(address _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupID) external onlyInGoodTimes nonReentrant returns (bytes32) {
        output = trade(msg.sender, BUYING, market, outcome, fxpAmount, fxpPrice, tradeGroupID)
        return(output : bytes32)
    }

    function publicSell(address _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupID) external onlyInGoodTimes nonReentrant returns (bytes32) {
        output = trade(msg.sender, SELLING, market, outcome, fxpAmount, fxpPrice, tradeGroupID)
        return(output : bytes32)
    }

    function publicTrade(uint8 _direction, address _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupID) external onlyInGoodTimes nonReentrant returns (bytes32) {
        output = trade(msg.sender, direction, market, outcome, fxpAmount, fxpPrice, tradeGroupID)
        return(output : bytes32)
    }

    function publicTakeBestOrder(uint8 _direction, address _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupID) external onlyInGoodTimes nonReentrant returns (uint256) {
        fxpAmountRemaining = takeBestOrder(msg.sender, direction, market, outcome, fxpAmount, fxpPrice, tradeGroupID)
        return(fxpAmountRemaining)
    }

    function trade(address _sender, uint8 _direction, address _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupID) internal returns (bytes32) {
        controller.assertIsWhitelisted(msg.sender)
        fxpAmount = takeBestOrder(sender, direction, market, outcome, fxpAmount, fxpPrice, tradeGroupID)
        if(fxpAmount > 0 and msg.gas >= MINIMUM_GAS_NEEDED):
            return (MAKEORDER.makeOrder(sender, direction, fxpAmount, fxpPrice, market, outcome, 0, 0, tradeGroupID) : bytes32)
        return (1 : bytes32)
    }

    function takeBestOrder(address _sender, uint8 _direction, address _market, uint8 _outcome, uint256 _fxpAmount, int256 _fxpPrice, uint256 _tradeGroupID) internal returns (uint256) {
        controller.assertIsWhitelisted(msg.sender)
        require(direction == BUYING or direction == SELLING)
        # we need to take a BID (1) if we want to SELL (2) and we need to take an ASK (2) if we want to BUY (1)
        type = (not (direction - 1)) + 1
        orderID = ORDERS.getBestOrderId(type, market, outcome)
        while(orderID != 0 and fxpAmount > 0 and msg.gas >= MINIMUM_GAS_NEEDED):
            fxpOrderPrice = ORDERS.getPrice(orderID, type, market, outcome)
            if type == BID:
                isAcceptablePrice = fxpOrderPrice >= fxpPrice
            if type == ASK:
                isAcceptablePrice = fxpOrderPrice <= fxpPrice
            if isAcceptablePrice:
                ORDERS.setPrice(market, outcome, fxpOrderPrice)
                ORDERS.modifyMarketVolume(market, fxpAmount)
                orderOwner = ORDERS.getOrderOwner(orderID, type, market, outcome)
                nextOrderID = ORDERS.getWorseOrderId(orderID, type, market, outcome)
                if(orderOwner != sender):
                    fxpAmount = TAKEORDER.takeOrder(sender, orderID, type, market, outcome, fxpAmount, tradeGroupID)
                orderID = nextOrderID
            else:
                orderID = 0
        return(fxpAmount)
    }
}
