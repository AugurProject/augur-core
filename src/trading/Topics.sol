// Copyright (C) 2015 Forecast Foundation OU, full GPL notice in LICENSE

pragma solidity ^0.4.13;

import 'ROOT/libraries/Typed.sol';
import 'ROOT/factories/IterableMapFactory.sol';
import 'ROOT/libraries/token/VariableSupplyToken.sol';
import 'ROOT/libraries/math/SafeMathUint256.sol';
import 'ROOT/libraries/Initializable.sol';
import 'ROOT/trading/ITopics.sol';


contract Topics is DelegationTarget, Typed, Initializable, ITopics {
    using SafeMathUint256 for uint256;

    // Mapping of topic to popularity
    IIterableMap private topics;

    function initialize() public beforeInitialized returns (bool) {
        endInitialization();
        topics = IterableMapFactory(controller.lookup("IterableMapFactory")).createIterableMap(controller, this);
        return true;
    }

    function getTypeName() public constant returns (bytes32) {
        return "Topics";
    }

    function updatePopularity(bytes32 _topic, uint256 _fxpAmount) public onlyWhitelistedCallers afterInitialized returns (bool) {
        uint256 _oldAmount = topics.getByKeyOrZero(_topic);
        uint256 _newAmount = _oldAmount.add(_fxpAmount);
        topics.addOrUpdate(_topic, _newAmount);
        return true;
    }

    function getPopularity(bytes32 _topic) public constant afterInitialized returns (uint256) {
        return topics.getByKey(_topic);
    }

    function getTopicByOffset(uint256 _offset) public constant afterInitialized returns (bytes32) {
        return topics.getByOffset(_offset);
    }

    function getPopularityByOffset(uint256 _offset) public constant afterInitialized returns (uint256) {
        bytes32 _topic = getTopicByOffset(_offset);
        return topics.getByKey(_topic);
    }

    function count() public constant afterInitialized returns (uint256) {
        return topics.count();
    }
}
