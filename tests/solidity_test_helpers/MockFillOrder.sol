pragma solidity 0.4.17;


import 'trading/IFillOrder.sol';


contract MockFillOrder is IFillOrder {
    using SafeMathUint256 for uint256;

    bytes32 private publicFillOrderOrderIdValue;
    uint256 private publicFillOrderAmountFillerWantsValue;
    uint256 private publicFillOrderTradeGroupIdValue;
    address private fillOrderFillerValue;
    bytes32 private fillOrderOrderIdValue;
    uint256 private fillOrderAmountFillerWantsValue;
    uint256 private fillOrderTradeGroupIdValue;

    function publicFillOrder(bytes32 _orderId, uint256 _amountFillerWants, uint256 _tradeGroupId) external payable returns (uint256) {
        publicFillOrderOrderIdValue = _orderId;
        publicFillOrderAmountFillerWantsValue = _amountFillerWants;
        publicFillOrderTradeGroupIdValue = _tradeGroupId;
        return 100;
    }

    function fillOrder(address _filler, bytes32 _orderId, uint256 _amountFillerWants, uint256 _tradeGroupId) external returns (uint256) {
        fillOrderFillerValue = _filler;
        fillOrderOrderIdValue = _orderId;
        fillOrderAmountFillerWantsValue = _amountFillerWants;
        fillOrderTradeGroupIdValue = _tradeGroupId;
        return 100;
    }
}