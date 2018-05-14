import BN = require('bn.js');
import { expect } from "chai";
import { TestFixture } from './TestFixture';
import { LegacyRepMigrator, LegacyRepData } from '../libraries/LegacyRepMigrator';

describe("RepMigration", () => {
    let fixture: TestFixture;
    before(async () => {
        fixture = await TestFixture.create(true);
    });
    it("#repMigration", async () => {
        // The legacy rep contract must be paused prior to migration since we have to have the list of token owners and allowances ready and frozen
        await fixture.pauseLegacyRep();
        let legacyRepLocked = await fixture.isLegacyRepPaused();
        expect(legacyRepLocked).to.be.true;

        // The "real" REP contract is locked until migration occurs
        let repLocked = await fixture.isRepMigratingFromLegacy();
        expect(repLocked).to.be.true;

        const legacyRepData: LegacyRepData = {
            balances: [fixture.accountManager.defaultAddress],
            allowanceOwners: [],
            allowanceSpenders: [],
        };

        // Before we run the migration which will freeze legacy REP lets create some balances and approvals
        for (let i = 0; i < 5; i++) {
            const amount = new BN(i + 1);
            const address = `0x000000000000000000000000000000000000000${i}`;

            await fixture.transferLegacyRep(address, amount);
            await fixture.approveLegacyRep(address, amount);

            const balance = await fixture.getLegacyRepBalance(address);
            const allowance = await fixture.getLegacyRepAllowance(fixture.accountManager.defaultAddress, address);

            expect(balance.toNumber()).to.eq(amount.toNumber());
            expect(allowance.toNumber()).to.eq(amount.toNumber());

            legacyRepData.balances.push(address);
            legacyRepData.allowanceOwners.push(fixture.accountManager.defaultAddress);
            legacyRepData.allowanceSpenders.push(address);
        }

        // Now we can run the LegacyRepMigrator which will freeze the legacy REP contract and migrate allowances and balances to the new one, making it unlock. When running the script normally we'll be reading from a file and passing a large data structure but here we'll just pass in the data corresponding to the balances and allowances we created.
        const reputationTokenAddress = await fixture.universe.getReputationToken_();
        const txSize = 2;
        const legacyRepMigrator = await LegacyRepMigrator.create(legacyRepData, reputationTokenAddress, txSize);
        await legacyRepMigrator.migrateLegacyRep();

        repLocked = await fixture.isRepMigratingFromLegacy();
        expect(repLocked).to.be.false;

        for (let i = 0; i < 5; i++) {
            const amount = new BN(i + 1);
            const address = `0x000000000000000000000000000000000000000${i}`;

            const balance = await fixture.getRepBalance(address);
            const allowance = await fixture.getRepAllowance(fixture.accountManager.defaultAddress, address);

            expect(balance.toNumber()).to.eq(amount.toNumber());
            expect(allowance.toNumber()).to.eq(amount.toNumber());
        }
    });
});
