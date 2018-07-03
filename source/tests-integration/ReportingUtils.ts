import BN = require('bn.js');
import { expect } from "chai";
import { TestFixture } from './TestFixture';
import { Market } from '../libraries/ContractInterfaces';

const ZERO_ADDRESS = "0x0000000000000000000000000000000000000000";

export class ReportingUtils {
    public async proceedToDesignatedReporting(fixture: TestFixture, market: Market) {
        const marketEndTime = await market.getEndTime_();
        await fixture.setTimestamp(marketEndTime.add(new BN(1)));
    }

    public async proceedToInitialReporting(fixture: TestFixture, market: Market) {
        const designatedReportingEndTime = await market.getDesignatedReportingEndTime_();
        await fixture.setTimestamp(designatedReportingEndTime.add(new BN(1)));
    }

    // TODO: Add `contributor` param, like `proceedToNextRound` function in Python tests
    public async proceedToNextRound(fixture: TestFixture, market: Market, doGenerateFees: boolean = false, moveTimeForward: boolean = true, randomPayoutNumerators: boolean = false) {
        const currentTimestamp = await fixture.getTimestamp();
        const marketEndTime = await market.getEndTime_();
        if (currentTimestamp.lt(marketEndTime)) {
            const marketDesignatedReportingEndTime = await market.getDesignatedReportingEndTime_();
            await fixture.setTimestamp(marketDesignatedReportingEndTime.add(new BN(1)));
        }

        const feeWindowAddress = await market.getFeeWindow_();

        const numberOfOutcomes = await market.getNumberOfOutcomes_();
        const numTicks = await market.getNumTicks_();
        let payoutNumerators = new Array(numberOfOutcomes.toNumber()).fill(new BN(0));
        payoutNumerators[0] = numTicks;

        let winningPayoutHash = "";
        if (feeWindowAddress === ZERO_ADDRESS) {
            await market.doInitialReport(payoutNumerators, false);
            expect(await market.getFeeWindow_() === ZERO_ADDRESS).to.be.false;
            console.log("Submitted initial report");

            // Buy and sell complete sets to generate reporting fees
            let outcome = new BN(0);
            let numShares = new BN(10000000000000);
            // Buy complete sets
            await fixture.buyCompleteSets(market, numShares);
            let numOwnedShares = await fixture.getNumSharesInMarket(market, outcome);

            let ethBalance = await fixture.getEthBalance();
            console.log("ethBalance after buying complete set", ethBalance.toString(10));
            console.log("numOwnedShares after buying complete set", numOwnedShares.toString(10));

            // Sell Complete Sets
            ethBalance = await fixture.getEthBalance();
            console.log("ethBalance before selling complete set", ethBalance.toString(10));
            let numOwnedSharesBefore = await fixture.getNumSharesInMarket(market, outcome);
            console.log("numOwnedShares before selling complete set", numOwnedSharesBefore.toString(10));
            await fixture.sellCompleteSets(market, numShares);
            ethBalance = await fixture.getEthBalance();
            console.log("ethBalance before selling complete set", ethBalance.toString(10));
            numOwnedSharesBefore = await fixture.getNumSharesInMarket(market, outcome);
            console.log("numOwnedShares after selling complete set", numOwnedSharesBefore.toString(10));
        } else {
            const feeWindow = await fixture.getFeeWindow(market);
            const feeWindowStartTime = await feeWindow.getStartTime_();
            await fixture.setTimestamp(feeWindowStartTime.add(new BN(1)));
            // This will also use the InitialReporter which is not a DisputeCrowdsourcer, but has the called function from abstract inheritance
            const winningReport = await fixture.getWinningReportingParticipant(market);
            winningPayoutHash = await winningReport.getPayoutDistributionHash_();

            let chosenPayoutNumerators = [];
            if (randomPayoutNumerators) {
                chosenPayoutNumerators = new Array(numberOfOutcomes).fill(new BN(0));
                // Set chosenPayoutNumerators[0] to number >= 0 and <= numTicks
                chosenPayoutNumerators[0] = new BN(Math.floor(Math.random() * Math.floor(numTicks.toNumber() + 1)));
                chosenPayoutNumerators[1] = numTicks.sub(chosenPayoutNumerators[0]);
            } else {
                const firstReportWinning = await market.derivePayoutDistributionHash_(payoutNumerators, false) === winningPayoutHash;
                chosenPayoutNumerators = payoutNumerators;
                if (firstReportWinning) {
                    payoutNumerators.reverse();
                }
            }

            const chosenPayoutHash = await market.derivePayoutDistributionHash_(chosenPayoutNumerators, false);
            const participantStake = await market.getParticipantStake_();
            const stakeInOutcome = await market.getStakeInOutcome_(chosenPayoutHash);
            const amount = participantStake.mul(new BN(2)).sub(stakeInOutcome.mul(new BN(3)));
            await fixture.contribute(market, chosenPayoutNumerators, false, amount);
            console.log("Staked", amount.toString(10));
            console.log("Payout numerators", chosenPayoutNumerators);
            const forkingMarket = await market.getForkingMarket_();
            const marketFeeWindow = await market.getFeeWindow_();
            expect(forkingMarket !== ZERO_ADDRESS || marketFeeWindow !== feeWindowAddress).to.be.true;
        }

        if (doGenerateFees) {
            // TODO: Create and call `generateFees` function
        }

        if (moveTimeForward) {
            let feeWindow = await fixture.getFeeWindow(market);
            let feeWindowStartTime = await feeWindow.getStartTime_();
            await fixture.setTimestamp(feeWindowStartTime.add(new BN(1)));
        }
    }

    public async proceedToFork(fixture: TestFixture, market: Market) {
        let forkingMarket = await market.getForkingMarket_();
        let disputeRound = 0;
        while (forkingMarket === ZERO_ADDRESS) {
            console.log("\nStarted round", disputeRound);
            await this.proceedToNextRound(fixture, market);
            forkingMarket = await market.getForkingMarket_();
            disputeRound++;
        }

        let ethBalance = await fixture.getEthBalance();
        console.log("ethBalance before calling forkAndRedeem", ethBalance.toString(10));

        const numParticipants = await market.getNumParticipants_();
        for (let i = 0; i < numParticipants.toNumber(); i++) {
            const reportingParticipantAddress = await market.getReportingParticipant_(new BN(i));
            const reportingParticipant = await fixture.getReportingParticipant(reportingParticipantAddress);
            await reportingParticipant.forkAndRedeem();

            const reportingParticipantStake = await reportingParticipant.getStake_();
            expect(reportingParticipantStake === new BN(0));
        }

        ethBalance = await fixture.getEthBalance();
        console.log("ethBalance after calling forkAndRedeem", ethBalance.toString(10));

        console.log("\nCalled forkAndRedeem on reporting participants");
    }
}

