// Create market, make a trade on it, designated reporter reports, market is finalized, traders settle shares, reporters redeem tokens.
import { expect } from "chai";
import { compileAndDeployContracts } from "../deployment/deployContracts";
import { ContractDeployer } from "../libraries/ContractDeployer";
import { stringTo32ByteHex } from "../libraries/HelperFunctions";
import { Connector } from '../libraries/Connector';
import { Configuration } from '../libraries/Configuration';

describe("TradeAndReport", () => {
    var contractDeployer: ContractDeployer;
    before(async () => {
        const configuration = await Configuration.create();
        const connector = new Connector(configuration);
        contractDeployer = await compileAndDeployContracts(configuration, connector);
    });
    it("#tradeAndReport", async () => {
        const market = await contractDeployer.market;
        const actualTypeName = await market.getTypeName_();
        const expectedTypeName = stringTo32ByteHex("Market");
        expect(actualTypeName).to.equal(expectedTypeName);
    });
});
