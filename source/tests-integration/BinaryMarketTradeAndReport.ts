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

        const universe = contractDeployer.getUniverse();
        const cash = contractDeployer.getCash();
        //const createOrder = contracts["CreateOrder"];
        const createOrder = await parseAbiIntoMethods(contractDeployer.getEthjsQuery(), signatures["CreateOrder"], { to: contracts["CreateOrder"].address });
        const trade = contracts["Trade"];
        const fillOrder = contracts["FillOrder"];
        const orders = contracts["Orders"];
        const ordersFetcher = contracts["OrdersFetcher"];
        const market = contractDeployer.getBinaryMarket();
        const tradeGroupId = 42;

        const orderId = await padAndHexlify("", 40);
        // console.log(BID);
        // console.log(2);
        // console.log(fix('0.6'));
        // console.log(market.address);
        // console.log(YES);
        // console.log(orderId);
        // console.log(orderId);
        // console.log(tradeGroupId);
        // console.log(testAccounts[1].address);
        // console.log(fix(2, 0.6));

        const orderTxHash = await createOrder.publicCreateOrder.bind({ sender: testAccounts[1].address, from: testAccounts[1].address, value: fix(2, 0.6)})(BID, 2, fix(0.6), market.address, YES, orderId, orderId, tradeGroupId);
        console.log(orderTxHash);
        // let receiptLogs = await contractDeployer.getReceiptLogs(orderTxHash, "CreateOrder");
        // const order = await this.getContractFromAddress(receiptLogs[0].order, "Orders", this.testAccounts[0].address, this.gasAmount);
        // console.log(order);

        // const fillOrderId = trade.publicSell(market.address, YES, 2, fix(0.6), tradeGroupId, {sender: testAccounts[2].publicKey, value: fix(2, 0.4)});
        // console.log(fillOrderId);

        // assert ordersFetcher.getOrder(orderId) == [0L, 0L, longToHexString(0), 0L, 0L, longTo32Bytes(0), longTo32Bytes(0), 0L];
        // assert fillOrderId == longTo32Bytes(1);


        // const reputationToken = contractDeployer.applySignature('ReputationToken', universe.getReputationToken());
        // const reportingTokenNo = contractDeployer.getReportingToken(market, [Math.pow(10, 18),0]);
        // const reportingTokenYes = contractDeployer.getReportingToken(market, [0,Math.pow(10, 18)]);
        // const reportingWindow = contractDeployer.applySignature('ReportingWindow', universe.getNextReportingWindow());
        // const expectedMarketCreatorFeePayout = contracts["MarketFeeCalculator"].getValidityBond(reportingWindow.address);
        // const expectedReportingWindowFeePayout = contracts["MarketFeeCalculator"].getTargetReporterGasCosts(reportingWindow.address);
    });
});
