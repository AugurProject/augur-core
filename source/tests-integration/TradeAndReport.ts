// Create market, make a trade on it, designated reporter reports, market is finalized, traders settle shares, reporters redeem tokens.

import BN = require('bn.js');
import { expect } from "chai";
import { stringTo32ByteHex } from "../libraries/HelperFunctions";
import { TestFixture } from './TestFixture';

describe("TradeAndReport", () => {
    let fixture: TestFixture;
    before(async () => {
        fixture = await TestFixture.create();
    });
    it("#tradeAndReport", async () => {
        await fixture.approveCentralAuthority();

        // Create a market
        const market = await fixture.createReasonableMarket(fixture.universe, fixture.cash.address, [stringTo32ByteHex(" "), stringTo32ByteHex(" ")]);
        const actualTypeName = await market.getTypeName_();
        const expectedTypeName = stringTo32ByteHex("Market");
        expect(actualTypeName).to.equal(expectedTypeName);

        const numTicks = await market.getNumTicks_();

        // Place an order
        let type = new BN(0); // BID
        let outcome = new BN(0);
        let numShares = new BN(10000000000000);
        let price = new BN(2150);

        await fixture.placeOrder(market.address, type, numShares, price, outcome, stringTo32ByteHex(""), stringTo32ByteHex(""), stringTo32ByteHex("42"));

        const orderID = await fixture.getBestOrderId(type, market.address, outcome)

        const orderPrice = await fixture.getOrderPrice(orderID);
        expect(orderPrice.toNumber()).to.equal(price.toNumber());

        // Buy complete sets
        await fixture.buyCompleteSets(market, numShares);
        const numOwnedShares = await fixture.getNumSharesInMarket(market, outcome);
        expect(numOwnedShares.toNumber()).to.equal(numShares.toNumber());

        // Cancel the original rest of order
        await fixture.cancelOrder(orderID);
        const remainingAmount = await fixture.getOrderAmount(orderID);
        expect(remainingAmount.toNumber()).to.equal(0);

        // Proceed to reporting
        let newTimestamp = await market.getEndTime_();
        newTimestamp = newTimestamp.add(new BN(1));
        await fixture.setTimestamp(newTimestamp);
        const timestamp = await fixture.getTimestamp();
        expect(timestamp.toNumber()).to.equal(newTimestamp.toNumber());

        // Do designated report
        await fixture.doInitialReport(market, [numTicks, new BN(0)], false);

        const feeWindow = await fixture.getFeeWindow(market);
        const feeWindowStartTime = await feeWindow.getStartTime_();

        // Proceed to window start
        await fixture.setTimestamp(feeWindowStartTime.add(new BN(1)));

        // Dispute the outcome. The excess REP will simply not be used.
        await fixture.contribute(market, [new BN(0), numTicks], false, new BN(2).mul(new BN(10).pow(new BN(18))));
        const newFeeWindow = await fixture.getFeeWindow(market);
        expect(newFeeWindow.address).to.not.equal(feeWindow.address);

        // Finalize
        const newFeeWindowEndTime = await newFeeWindow.getEndTime_();
        await fixture.setTimestamp(newFeeWindowEndTime.add(new BN(1)));
        await fixture.finalizeMarket(market);
    });
});
