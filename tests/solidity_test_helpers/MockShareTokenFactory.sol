pragma solidity 0.4.18;


import 'libraries/Delegator.sol';
import 'reporting/IMarket.sol';
import 'IController.sol';


contract MockShareTokenFactory {
    IMarket private createShareTokenMarketValue;
    uint8 private createShareTokenOutcomeValue;
    uint8 private createShareTokenCounter;
    IShareToken[] private setCreateShareTokenValue;

    function resetCreateShareToken() public {
        createShareTokenCounter = 0;
    }

    function getCreateShareTokenCounter() public returns(uint8) {
        return createShareTokenCounter;
    }

    function getCreateShareToken(uint8 _index) public returns(IShareToken) {
        return setCreateShareTokenValue[_index];
    }

    function pushCreateShareToken(IShareToken _shareToken) public {
        setCreateShareTokenValue.push(_shareToken);
    }

    function getCreateShareTokenMarketValue() public returns(IMarket) {
        return createShareTokenMarketValue;
    }

    function getCreateShareTokenOutcomeValue() public returns(uint8) {
        return createShareTokenOutcomeValue;
    }
    
    function createShareToken(IController _controller, IMarket _market, uint8 _outcome) public returns (IShareToken) {
        createShareTokenMarketValue = _market;
        createShareTokenOutcomeValue = _outcome;
        createShareTokenCounter += 1;
        return setCreateShareTokenValue[_outcome];
    }
}
