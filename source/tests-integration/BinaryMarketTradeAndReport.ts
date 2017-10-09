// Create market, make a trade on it, designated reporter reports, market is finalized, traders settle shares, reporters redeem tokens.
import * as binascii from "binascii";
import { expect } from "chai";
import { ContractBlockchainData } from "contract-deployment";
import { BID, ASK, LONG, SHORT, YES, NO } from "./constants";
import { fix } from "./utils";
import { compileAndDeployContracts } from "../deployment/deployContracts";
import { parseAbiIntoMethods } from '../libraries/AbiParser';
import { ContractDeployer } from "../libraries/ContractDeployer";
import { TestAccount, generateTestAccounts, padAndHexlify } from "../libraries/HelperFunctions";


describe("BinaryMarketTradeAndReport", () => {
    var contractDeployer: ContractDeployer;
    beforeEach(async () => {
        contractDeployer = await compileAndDeployContracts();
    });
    it("#tradeAndReport", async () => {
        const testAccounts = contractDeployer.getTestAccounts();
        const signatures = contractDeployer.getSignatures();
        const contracts = contractDeployer.getContracts();
        const compiledContracts = contractDeployer.getCompiledContracts();
        const ethjsQuery = await contractDeployer.getEthjsQuery();

        const universe = contractDeployer.getUniverse();
        const cash = contractDeployer.getCash();
        const createOrder = contracts["CreateOrder"];
        const trade = contracts["Trade"];
        const fillOrder = contracts["FillOrder"];
        const orders = contracts["Orders"];
        const ordersFetcher = contracts["OrdersFetcher"];
        const marketAddress = contractDeployer.getBinaryMarket();
        const tradeGroupId = 42;

        const orderId = await padAndHexlify("", 40);

        // TODO: Finish creating/filling an order and reporting on the market.  The line below is causing an rpc error.
        // const order = await createOrder.publicCreateOrder(BID, 2, fix(0.6), marketAddress, YES, orderId, orderId, tradeGroupId, { sender: testAccounts[1].address, value: fix(2, 0.6) });
        // console.log(order);
    });
});
