// Create market, make a trade on it, designated reporter reports, market is finalized, traders settle shares, reporters redeem tokens.
import { expect } from "chai";
import { ContractBlockchainData } from "contract-deployment";
import { BID, ASK, LONG, SHORT, YES, NO } from "./constants";
import { fix } from "./utils";
import { compileAndDeployContracts } from "../deployment/deployContracts";
import { parseAbiIntoMethods } from '../libraries/AbiParser';
import { ContractDeployer } from "../libraries/ContractDeployer";
import { TestAccount, generateTestAccounts, padAndHexlify, stringTo32ByteHex } from "../libraries/HelperFunctions";
import { Connector } from '../libraries/Connector';

describe("TradeAndReport", () => {
    var contractDeployer: ContractDeployer;
    before(async () => {
        const connector = new Connector();
        const ethjsQuery = await connector.waitUntilConnected();
    });
    beforeEach(async () => {
        contractDeployer = await compileAndDeployContracts();
    });
    it("#tradeAndReport", async () => {
        const market = await contractDeployer.market;
        const actualTypeName = await market.getTypeName();
        const expectedTypeName = stringTo32ByteHex("Market");
        expect(actualTypeName).to.equal(expectedTypeName);
    });
});
