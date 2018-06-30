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
        let timestamp = await fixture.getTimestamp();
        expect(timestamp.toNumber()).to.equal(newTimestamp.toNumber());

        // Do designated report
        await fixture.doInitialReport(market, [numTicks, new BN(0)], false);

        const feeWindow = await fixture.getFeeWindow(market);
        const feeWindowStartTime = await feeWindow.getStartTime_();

        // Proceed to window start
        await fixture.setTimestamp(feeWindowStartTime.add(new BN(1)));

        // Dispute the outcome. The excess REP will simply not be used.
        let disputeRound = 1;
        let totalContributedOutcome0 =  new BN(1).mul(new BN(10).pow(new BN(18)));
        let totalContributedOutcome1 = new BN(2).mul(new BN(10).pow(new BN(18)));
        let contributeAmount = totalContributedOutcome0;
        let payoutNumerators = [];
        const reputationToken = await fixture.getReputationToken();
        const totalTheoreticalSupply = await reputationToken.getTotalTheoreticalSupply_();
        const forkThreshold = totalTheoreticalSupply.div(new BN(40));
        let newFeeWindow = await fixture.getFeeWindow(market);
        let newFeeWindowStartTime = await newFeeWindow.getStartTime_();
        while (totalContributedOutcome0.div(new BN(2)).lt(forkThreshold) && totalContributedOutcome1.div(new BN(2)).lt(forkThreshold)) {
            if (disputeRound % 2 == 1) {
                payoutNumerators = [new BN(0), numTicks];
                totalContributedOutcome1 = totalContributedOutcome0.mul(new BN(2));
                contributeAmount = totalContributedOutcome1;
            } else {
                payoutNumerators = [numTicks, new BN(0)];
                totalContributedOutcome0 = totalContributedOutcome1.mul(new BN(2));
                contributeAmount = totalContributedOutcome0;
            }
            // console.log("Dispute Round:", disputeRound);
            // console.log("totalContributedOutcome0", totalContributedOutcome0.toString(10));
            // console.log("totalContributedOutcome1", totalContributedOutcome1.toString(10));
            // console.log("contributeAmount", contributeAmount.toString(10));
            // console.log("Payout Numerators:");
            // console.log(payoutNumerators);

            await fixture.contribute(market, payoutNumerators, false, contributeAmount);

            contributeAmount = contributeAmount.mul(new BN(2));
            disputeRound++;

            newFeeWindow = await fixture.getFeeWindow(market);
            expect(newFeeWindow.address).to.not.equal(feeWindow.address);
            newFeeWindowStartTime = await newFeeWindow.getStartTime_();
            await fixture.setTimestamp(newFeeWindowStartTime.add(new BN(1)));
        }

        const isForking = await fixture.isForking();
        expect(isForking).to.be.true;

        const repAmountToMigrate = new BN(9000000).mul(new BN(10).pow(new BN(18)));
        await fixture.migrateOutByPayout(reputationToken, [numTicks, new BN(0)], false, repAmountToMigrate);

        const payoutDistributionHash = await fixture.derivePayoutDistributionHash(market, [numTicks, new BN(0)], false);
        const childUniverseReputationToken = await fixture.getChildUniverseReputationToken(payoutDistributionHash);
        const reputationTotalMigrated = await childUniverseReputationToken.getTotalMigrated_();
        expect(reputationTotalMigrated.toString(10)).to.equal(repAmountToMigrate.toString(10));

        let isFinalized = await market.isFinalized_();
        expect(isFinalized).to.be.true;
    });
});
