// Create market, make a trade on it, designated reporter reports, market is finalized, traders settle shares, reporters redeem tokens.
import * as binascii from "binascii";
import { expect } from "chai";
import { ContractBlockchainData } from "contract-deployment";
import { BID, ASK, LONG, SHORT, YES, NO } from "./constants";
import { fix } from "./utils";
import { compileAndDeployContracts } from "../deployment/deployContracts";
import { ContractDeployer } from "../libraries/ContractDeployer";
import { TestAccount, generateTestAccounts, padAndHexlify } from "../libraries/HelperFunctions";


describe("BinaryMarketTradeAndReport", () => {
    var contractDeployer: ContractDeployer;
    beforeEach(async () => {
        contractDeployer = await compileAndDeployContracts();
    });
    it("#tradeAndReport", async () => {
        const testAccounts = contractDeployer.getTestAccounts();
        const contracts = await contractDeployer.getContracts();

        const cash = contractDeployer.getCash();
        const createOrder = contracts["CreateOrder"];
        const trade = contracts["Trade"];
        const fillOrder = contracts["FillOrder"];
        const orders = contracts["Orders"];
        const ordersFetcher = contracts["OrdersFetcher"];
        const market = contractDeployer.getBinaryMarket();
        const tradeGroupId = 42;

        // const orderId = createOrder.publicCreateOrder(BID, 2, fix(0.6), market.address, YES, await padAndHexlify("0", 32), await padAndHexlify("0", 32), tradeGroupId, { sender: testAccounts[1].publicKey, value: fix(2, 0.6)});
        // console.log(orderId);

        // const universe = contractDeployer.getUniverse();
        // const reputationToken = contractDeployer.applySignature('ReputationToken', universe.getReputationToken());
        // const reportingTokenNo = contractDeployer.getReportingToken(market, [Math.pow(10, 18),0]);
        // const reportingTokenYes = contractDeployer.getReportingToken(market, [0,Math.pow(10, 18)]);
        // const reportingWindow = contractDeployer.applySignature('ReportingWindow', universe.getNextReportingWindow());
        // const expectedMarketCreatorFeePayout = contracts["MarketFeeCalculator"].getValidityBond(reportingWindow.address);
        // const expectedReportingWindowFeePayout = contracts["MarketFeeCalculator"].getTargetReporterGasCosts(reportingWindow.address);
    });
});
