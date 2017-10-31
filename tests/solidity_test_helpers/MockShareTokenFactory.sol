pragma solidity 0.4.17;


import 'libraries/Delegator.sol';
import 'reporting/IMarket.sol';
import 'IController.sol';


contract MockShareTokenFactory {
    IMarket private createShareTokenMarketValue;
    uint8 private createShareTokenOutcomeValue;
    IShareToken private setCreateShareTokenValue;

    function setCreateShareToken(IShareToken _shareToken) public {
        setCreateShareTokenValue = _shareToken;
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
        return setCreateShareTokenValue;
    }
}
