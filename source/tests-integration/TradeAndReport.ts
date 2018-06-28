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
        let disputeRound = 1;
        let contributeAmount = new BN(2).mul(new BN(10).pow(new BN(18)));
        let reputationToken = await fixture.getReputationToken();
        console.log("reputationToken!!!!!!:", reputationToken);
        // const targetSupply = await fixture.getTargetSupply(reputationToken);
        const forkThreshold = new BN(550000).mul(new BN(10).pow(new BN(18)));
        let newFeeWindow = await fixture.getFeeWindow(market);
        let newFeeWindowStartTime = await newFeeWindow.getStartTime_();
        // console.log("contributeAmount", contributeAmount.toString(10));
        // console.log("forkThreshold", forkThreshold.toString(10));
        // console.log("newFeeWindowStartTime", newFeeWindowStartTime.toString(10));
        while (contributeAmount.lt(forkThreshold)) {
            let payoutNumerators = (disputeRound % 2 == 1) ? [new BN(0), numTicks] : [numTicks, new BN(0)];
            console.log("Dispute Round:", disputeRound);
            console.log("contributeAmount", contributeAmount.toString(10));
            console.log("Payout Numerators:");
            console.log(payoutNumerators);

            await fixture.contribute(market, payoutNumerators, false, contributeAmount);

            contributeAmount = contributeAmount.mul(new BN(2));
            disputeRound++;

            newFeeWindow = await fixture.getFeeWindow(market);
            expect(newFeeWindow.address).to.not.equal(feeWindow.address);
            newFeeWindowStartTime = await newFeeWindow.getStartTime_();
            console.log("newFeeWindowStartTime", newFeeWindowStartTime.toString(10));
            await fixture.setTimestamp(newFeeWindowStartTime.add(new BN(1)));
        }

        // const initialReporter = await fixture.getInitialReporter(market);
        // console.log("initialReporter", initialReporter);

        await fixture.contribute(market, [numTicks, new BN(0)], false, new BN(287856).mul(new BN(10).pow(new BN(18))));

        let isForking = await fixture.isForking();
        if (isForking) {
            console.log("Is forking");
        }

        const payoutDistributionHash = await fixture.derivePayoutDistributionHash(market, [numTicks, new BN(0)], false);
        console.log("payoutDistributionHash", payoutDistributionHash);

        // const forkingMarket = await fixture.getForkingMarket();
        // console.log("forkingMarket", forkingMarket);

        // const disputeCrowdsourcer = await fixture.getWinningReportingParticipant(market);
        // console.log("disputeCrowdsourcer", disputeCrowdsourcer);
console.log("Before migrateOut");
        await fixture.migrateOutByPayout(reputationToken, [new BN(0), numTicks], false, new BN(90000000));
console.log("After migrateOut");
        reputationToken = await fixture.getChildUniverseReputationToken(payoutDistributionHash);
        const reputationTotalMigrated = await reputationToken.getTotalMigrated_();
        console.log("reputationTotalMigrated:", reputationTotalMigrated.toString(10));
        const reputationTotalTheoreticalSupply = await reputationToken.getTotalTheoreticalSupply_();
        console.log("reputationTotalMigrated:", reputationTotalTheoreticalSupply.toString(10));

        // Finalize
        // const newFeeWindowEndTime = await newFeeWindow.getEndTime_();
        // await fixture.setTimestamp(newFeeWindowEndTime.add(new BN(1)));
        // await fixture.finalizeMarket(market);
    });
});
