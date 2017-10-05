// Create market, make a trade on it, designated reporter reports, market is finalized, traders settle shares, reporters redeem tokens.
import * as binascii from "binascii";
import { expect } from "chai";
import { ContractBlockchainData } from "contract-deployment";
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
        const controller = contractDeployer.getController();
        const contracts = await contractDeployer.getContracts();
        const universe = contractDeployer.getUniverse();

        // const reportingTokenNo = contractDeployer.getReportingToken(market, [10**18,0]);
        // const reportingTokenYes = contractDeployer.getReportingToken(market, [0,10**18]);
        // const reportingWindow = contractDeployer.applySignature('ReportingWindow', universe.getNextReportingWindow());
        // const expectedMarketCreatorFeePayout = contractDeployer.uploadedContracts["MarketFeeCalculator"].getValidityBond(reportingWindow.address);
        // const expectedReportingWindowFeePayout = contractDeployer.uploadedContracts["MarketFeeCalculator"].getTargetReporterGasCosts(reportingWindow.address);
    });
});
