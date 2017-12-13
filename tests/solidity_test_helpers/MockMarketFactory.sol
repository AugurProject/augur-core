pragma solidity 0.4.18;

import 'reporting/IFeeWindow.sol';
import 'reporting/IMarket.sol';
import 'reporting/IReputationToken.sol';
import 'trading/ICash.sol';
import 'IController.sol';
import 'Augur.sol';


contract MockMarketFactory {
    IMarket private setMarketValue;
    IController private createMarketControllerValue;
    IFeeWindow private createMarketFeeWindowValue;
    uint256 private createMarketEndTimeValue;
    uint8 private createMarketNumOutcomesValue;
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

    function getCreateMarketFeeWindowValue() public returns(IFeeWindow) {
        return createMarketFeeWindowValue;
    }

    function getCreateMarketEndTimeValue() public returns(uint256) {
        return createMarketEndTimeValue;
    }

    function getCreateMarketNumOutcomesValue() public returns(uint8) {
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

    function createMarket(IController _controller, IFeeWindow _feeWindow, uint256 _endTime, uint8 _numOutcomes, uint256 _numTicks, uint256 _feePerEthInWei, ICash _denominationToken, address _creator, address _designatedReporterAddress) public payable returns (IMarket _market) {
        createMarketControllerValue = _controller;
        createMarketFeeWindowValue = _feeWindow;
        createMarketEndTimeValue = _endTime;
        createMarketNumOutcomesValue = _numOutcomes;
        createMarketNumTicksValue = _numTicks;
        createMarketfeePerEthInWeiValue = _feePerEthInWei;
        createMarketDenominationTokenValue = _denominationToken;
        createMarketCreatorValue = _creator;
        createMarketDesignatedReporterAddressValue = _designatedReporterAddress;
        return setMarketValue;
    }
}
