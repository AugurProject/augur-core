pragma solidity 0.4.20;

import 'reporting/IFeeWindow.sol';
import 'reporting/IMarket.sol';
import 'reporting/IReputationToken.sol';
import 'trading/ICash.sol';
import 'IController.sol';


contract MockMarketFactory {
    IMarket private setMarketValue;
    IController private createMarketControllerValue;
    IUniverse private createMarketUniverseValue;
    uint256 private createMarketEndTimeValue;
    uint256 private createMarketNumOutcomesValue;
    uint256 private createMarketNumTicksValue;
    uint256 private createMarketfeePerEthInWeiValue;
    ICash private createMarketDenominationTokenValue;
    address private createMarketCreatorValue;
    address private createMarketDesignatedReporterAddressValue;

    function setMarket(IMarket _market) public {
        setMarketValue = _market;
    }

    function getCreateMarketController() public returns(IController) {
        return createMarketControllerValue;
    }

    function getCreateMarketUniverseValue() public returns(IUniverse) {
        return createMarketUniverseValue;
    }

    function getCreateMarketEndTimeValue() public returns(uint256) {
        return createMarketEndTimeValue;
    }

    function getCreateMarketNumOutcomesValue() public returns(uint256) {
        return createMarketNumOutcomesValue;
    }

    function getCreateMarketNumTicksValue() public returns(uint256) {
        return createMarketNumTicksValue;
    }

    function getCreateMarketfeePerEthInWeiValue() public returns(uint256) {
        return createMarketfeePerEthInWeiValue;
    }

    function getCreateMarketDenominationTokenValue() public returns(ICash) {
        return createMarketDenominationTokenValue;
    }

    function getCreateMarketCreatorValue() public returns(address) {
        return createMarketCreatorValue;
    }

    function getCreateMarketDesignatedReporterAddressValue() public returns(address) {
        return createMarketDesignatedReporterAddressValue;
    }

    function createMarket(IController _controller, IUniverse _universe, uint256 _endTime, uint256 _feePerEthInWei, ICash _denominationToken, address _designatedReporterAddress, address _sender, uint256 _numOutcomes, uint256 _numTicks) public payable returns (IMarket _market) {
        createMarketControllerValue = _controller;
        createMarketUniverseValue = _universe;
        createMarketEndTimeValue = _endTime;
        createMarketNumOutcomesValue = _numOutcomes;
        createMarketNumTicksValue = _numTicks;
        createMarketfeePerEthInWeiValue = _feePerEthInWei;
        createMarketDenominationTokenValue = _denominationToken;
        createMarketCreatorValue = _sender;
        createMarketDesignatedReporterAddressValue = _designatedReporterAddress;
        return setMarketValue;
    }
}
