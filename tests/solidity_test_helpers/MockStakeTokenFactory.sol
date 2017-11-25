pragma solidity 0.4.18;


import 'libraries/Delegator.sol';
import 'reporting/IMarket.sol';
import 'IController.sol';
import 'libraries/collections/Map.sol';
import 'reporting/IStakeToken.sol';
import 'factories/MapFactory.sol';


contract MockStakeTokenFactory {
    IMarket private createStakeTokenMarketValue;
    uint256[] private createStakeTokenPayoutValue;
    uint8 private createStakeTokenCounter;
    Map private mapStakeTokenValue;   
    bytes32 private createDistroHashValue; 

    function getCreateStakeTokenCount() public returns(uint256) {
        return mapStakeTokenValue.getCount();
    }

    function getCreateStakeToken(bytes32 _payoutDistributionHash) public returns(IStakeToken) {
        return IStakeToken(mapStakeTokenValue.getAsAddressOrZero(_payoutDistributionHash));
    }

    function setStakeToken(bytes32 _payoutDistributionHash, IStakeToken _stakeToken) public {
        mapStakeTokenValue.add(_payoutDistributionHash, _stakeToken);
    }

    function getCreateDistroHashValue() public returns(bytes32) {
        return createDistroHashValue;
    }

    function initializeMap(IController _controller) public returns(bool) {
        mapStakeTokenValue = MapFactory(_controller.lookup("MapFactory")).createMap(_controller, this);
        return true;
    }

    function getStakeTokenMap() public returns(Map) {
        return mapStakeTokenValue;
    }

    function getCreateStakeTokenMarketValue() public returns(IMarket) {
        return createStakeTokenMarketValue;
    }

    function getCreateStakeTokenPayoutValue() public returns(uint256[]) {
        return createStakeTokenPayoutValue;
    }
    
    function createStakeToken(IController _controller, IMarket _market, uint256[] _payoutNumerators, bool _invalid) public returns (IStakeToken) {
        createStakeTokenMarketValue = _market;
        createStakeTokenPayoutValue = _payoutNumerators;     
        createDistroHashValue = _market.derivePayoutDistributionHash(_payoutNumerators, _invalid);
        return getCreateStakeToken(createDistroHashValue);
    }
}
