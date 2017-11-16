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
        const market = await fixture.createReasonableMarket(fixture.universe, fixture.cash.address, new BN(2));
        const actualTypeName = await market.getTypeName_();
        const expectedTypeName = stringTo32ByteHex("Market");
        expect(actualTypeName).to.equal(expectedTypeName);
    });
});
