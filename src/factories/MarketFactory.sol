pragma solidity ^0.4.11;

import 'ROOT/libraries/Delegator.sol';


// FIXME: remove once this can be imported as a solidty contract
contract Market {
    function initialize(address reportingWindow, int256 endTime, int256 numOutcomes, int256 payoutDenominator, int256 feePerEthInWei, address denominationToken, address creator, int256 minDisplayPrice, int256 maxDisplayPrice, address automatedReporterAddress, int256 topic) payable;
}


contract MarketFactory {

    function createMarket(address controller, address reportingWindow, int256 endTime, int256 numOutcomes, int256 payoutDenominator, int256 feePerEthInWei, address denominationToken, address creator, int256 minDisplayPrice, int256 maxDisplayPrice, address automatedReporterAddress, int256 topic) payable returns (Market market) {
        Delegator del = new Delegator(controller, "market");
        market = Market(del);
        market.initialize.value(msg.value)(reportingWindow, endTime, numOutcomes, payoutDenominator, feePerEthInWei, denominationToken, creator, minDisplayPrice, maxDisplayPrice, automatedReporterAddress, topic);
        return market;
    }
}