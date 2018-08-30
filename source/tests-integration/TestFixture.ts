import BN = require('bn.js');
import { TestRpc } from './TestRpc';
import { Connector } from '../libraries/Connector';
import { AccountManager } from '../libraries/AccountManager';
import { ContractCompiler } from '../libraries/ContractCompiler';
import { ContractDeployer } from '../libraries/ContractDeployer';
import { CompilerConfiguration } from '../libraries/CompilerConfiguration';
import { DeployerConfiguration } from '../libraries/DeployerConfiguration';
import { NetworkConfiguration } from '../libraries/NetworkConfiguration';
import { FeeWindow, ShareToken, ClaimTradingProceeds, CompleteSets, TimeControlled, Cash, Universe, Market, CreateOrder, Orders, Trade, CancelOrder, LegacyReputationToken, DisputeCrowdsourcer, ReputationToken, } from '../libraries/ContractInterfaces';
import { stringTo32ByteHex } from '../libraries/HelperFunctions';

export class TestFixture {
    private static GAS_PRICE: BN = new BN(1);

    private readonly connector: Connector;
    public readonly accountManager: AccountManager;
    // FIXME: extract out the bits of contract deployer that we need access to, like the contracts/abis, so we can have a more targeted dependency
    public readonly contractDeployer: ContractDeployer;
    public readonly testRpc: TestRpc | null;
    public readonly sdbEnabled: boolean;

    public get universe() { return this.contractDeployer.universe; }
    public get cash() { return <Cash> this.contractDeployer.getContract('Cash'); }

    public constructor(connector: Connector, accountManager: AccountManager, contractDeployer: ContractDeployer, testRpc: TestRpc | null, sdbEnabled: boolean) {
        this.connector = connector;
        this.accountManager = accountManager;
        this.contractDeployer = contractDeployer;
        this.testRpc = testRpc;
        this.sdbEnabled = sdbEnabled;
    }

    public static create = async (pretendToBeProduction: boolean = false): Promise<TestFixture> => {
        const networkConfiguration = NetworkConfiguration.create();
        const compilerConfiguration = CompilerConfiguration.create()

        const testRpc = await TestRpc.startTestRpcIfNecessary(networkConfiguration, compilerConfiguration);

        const compiledContracts = await new ContractCompiler(compilerConfiguration).compileContracts();

        const connector = new Connector(networkConfiguration);
        console.log(`Waiting for connection to: ${networkConfiguration.networkName} at ${networkConfiguration.http}`);
        await connector.waitUntilConnected();
        const accountManager = new AccountManager(connector, networkConfiguration.privateKey);

        const deployerConfiguration = DeployerConfiguration.createWithControlledTime();
        let contractDeployer = new ContractDeployer(deployerConfiguration, connector, accountManager, compiledContracts);

        if (pretendToBeProduction) {
            const legacyRepAddress = await contractDeployer.uploadLegacyRep();
            await contractDeployer.initializeLegacyRep();

            const fakeProdDeployerConfiguration = DeployerConfiguration.createWithControlledTime(legacyRepAddress, true);
            contractDeployer = new ContractDeployer(fakeProdDeployerConfiguration, connector, accountManager, compiledContracts);
        }

        const addressMapping = await contractDeployer.deploy();

         if (testRpc !== null && compilerConfiguration.enableSdb) {
            await testRpc.linkDebugSymbols(compiledContracts, addressMapping);
        }

        const testFixture = new TestFixture(connector, accountManager, contractDeployer, testRpc, compilerConfiguration.enableSdb);
        await testFixture.linkDebugSymbolsForContract('Universe', testFixture.contractDeployer.universe.address);

        return testFixture;
    }

    public async linkDebugSymbolsForContract(contractName: string, contractAddress: string): Promise<void> {
        if (this.sdbEnabled && this.testRpc !== null) {
            await this.testRpc.linkContractAddress(contractName, contractAddress);
        }
    }

    public async approveCentralAuthority(): Promise<void> {
        const authority = this.contractDeployer.getContract('Augur');
        const cash = new Cash(this.connector, this.accountManager, this.contractDeployer.getContract('Cash').address, TestFixture.GAS_PRICE);
        await cash.approve(authority.address, new BN(2).pow(new BN(256)).sub(new BN(1)));
    }

    public async createMarket(universe: Universe, outcomes: string[], endTime: BN, feePerEthInWei: BN, denominationToken: string, designatedReporter: string): Promise<Market> {
        const marketCreationFee = await universe.getOrCacheMarketCreationCost_();

        console.log("Creating Market");
        const marketAddress = await universe.createCategoricalMarket_(endTime, feePerEthInWei, denominationToken, designatedReporter, outcomes, stringTo32ByteHex(" "), 'description', '', { attachedEth: marketCreationFee });
        if (!marketAddress || marketAddress == "0x") {
            throw new Error("Unable to get address for new categorical market.");
        }
        await universe.createCategoricalMarket(endTime, feePerEthInWei, denominationToken, designatedReporter, outcomes, stringTo32ByteHex(" "), 'description', '', { attachedEth: marketCreationFee });
        const market = new Market(this.connector, this.accountManager, marketAddress, TestFixture.GAS_PRICE);
        if (await market.getTypeName_() !== stringTo32ByteHex("Market")) {
            throw new Error("Unable to create new categorical market");
        }
        await this.linkDebugSymbolsForContract('Market', market.address);
        return market;
    }

    public async createReasonableMarket(universe: Universe, denominationToken: string, outcomes: string[]): Promise<Market> {
        const endTime = new BN(Math.round(new Date().getTime() / 1000) + 30 * 24 * 60 * 60);
        const fee = (new BN(10)).pow(new BN(16));
        return await this.createMarket(universe, outcomes, endTime, fee, denominationToken, this.accountManager.defaultAddress);
    }

    public async placeOrder(market: string, type: BN, numShares: BN, price: BN, outcome: BN, betterOrderID: string, worseOrderID: string, tradeGroupID: string): Promise<void> {
        const createOrderContract = await this.contractDeployer.getContract("CreateOrder");
        const createOrder = new CreateOrder(this.connector, this.accountManager, createOrderContract.address, TestFixture.GAS_PRICE);

        const ethValue = numShares.mul(price);

        await createOrder.publicCreateOrder(type, numShares, price, market, outcome, betterOrderID, worseOrderID, tradeGroupID, { attachedEth: ethValue });
        return;
    }

    public async takeBestOrder(marketAddress: string, type: BN, numShares: BN, price: BN, outcome: BN, tradeGroupID: string): Promise<void> {
        const tradeContract = await this.contractDeployer.getContract("Trade");
        const trade = new Trade(this.connector, this.accountManager, tradeContract.address, TestFixture.GAS_PRICE);

        let actualPrice = price;
        if (type == new BN(1)) {
            const market = new Market(this.connector, this.accountManager, marketAddress, TestFixture.GAS_PRICE);
            const numTicks = await market.getNumTicks_();
            actualPrice = numTicks.sub(price);
        }
        const ethValue = numShares.mul(actualPrice);

        const bestPriceAmount = await trade.publicFillBestOrder_(type, marketAddress, outcome, numShares, price, tradeGroupID, { attachedEth: ethValue });
        if (bestPriceAmount == new BN(0)) {
            throw new Error("Could not take best Order");
        }

        await trade.publicFillBestOrder(type, marketAddress, outcome, numShares, price, tradeGroupID, { attachedEth: ethValue });
        return;
    }

    public async cancelOrder(orderID: string): Promise<void> {
        const cancelOrderContract = await this.contractDeployer.getContract("CancelOrder");
        const cancelOrder = new CancelOrder(this.connector, this.accountManager, cancelOrderContract.address, TestFixture.GAS_PRICE);

        await cancelOrder.cancelOrder(orderID);
        return;
    }

    public async claimTradingProceeds(market: Market, shareholder: string): Promise<void> {
        const claimTradingProceedsContract = await this.contractDeployer.getContract("ClaimTradingProceeds");
        const claimTradingProceeds = new ClaimTradingProceeds(this.connector, this.accountManager, claimTradingProceedsContract.address, TestFixture.GAS_PRICE);
        await claimTradingProceeds.claimTradingProceeds(market.address, shareholder);
        return;
    }

    public async getOrderPrice(orderID: string): Promise<BN> {
        const ordersContract = await this.contractDeployer.getContract("Orders");
        const orders = new Orders(this.connector, this.accountManager, ordersContract.address, TestFixture.GAS_PRICE);

        const price = await orders.getPrice_(orderID);
        if (price.toNumber() == 0) {
            throw new Error("Unable to get order price");
        }
        return price;
    }

    public async getOrderAmount(orderID: string): Promise<BN> {
        const ordersContract = await this.contractDeployer.getContract("Orders");
        const orders = new Orders(this.connector, this.accountManager, ordersContract.address, TestFixture.GAS_PRICE);
        return await orders.getAmount_(orderID);
    }

    public async getBestOrderId(type: BN, market: string, outcome: BN): Promise<string> {
        const ordersContract = await this.contractDeployer.getContract("Orders");
        const orders = new Orders(this.connector, this.accountManager, ordersContract.address, TestFixture.GAS_PRICE);

        const orderID = await orders.getBestOrderId_(type, market, outcome);
        if (!orderID) {
            throw new Error("Unable to get order price");
        }
        return orderID;
    }

    public async buyCompleteSets(market: Market, amount: BN): Promise<void> {
        const completeSetsContract = await this.contractDeployer.getContract("CompleteSets");
        const completeSets = new CompleteSets(this.connector, this.accountManager, completeSetsContract.address, TestFixture.GAS_PRICE);

        const numTicks = await market.getNumTicks_();
        const ethValue = amount.mul(numTicks);

        await completeSets.publicBuyCompleteSets(market.address, amount, { attachedEth: ethValue });
        return;
    }

    public async sellCompleteSets(market: Market, amount: BN): Promise<void> {
        const completeSetsContract = await this.contractDeployer.getContract("CompleteSets");
        const completeSets = new CompleteSets(this.connector, this.accountManager, completeSetsContract.address, TestFixture.GAS_PRICE);

        await completeSets.publicSellCompleteSets(market.address, amount);
        return;
    }

    public async contribute(market: Market, payoutNumerators: Array<BN>, invalid: boolean, amount: BN): Promise<void> {
        await market.contribute(payoutNumerators, invalid, amount, "");
        return;
    }

    public async derivePayoutDistributionHash(market: Market, payoutNumerators: Array<BN>, invalid: boolean): Promise<string> {
        return await market.derivePayoutDistributionHash_(payoutNumerators, invalid);
    }

    public async isForking(): Promise<boolean> {
        return await this.universe.isForking_();
    }

    public async migrateOutByPayout(reputationToken: ReputationToken, payoutNumerators: Array<BN>, invalid: boolean, attotokens: BN) {
        await reputationToken.migrateOutByPayout(payoutNumerators, invalid, attotokens);
        return;
    }

    public async getNumSharesInMarket(market: Market, outcome: BN): Promise<BN> {
        const shareTokenAddress = await market.getShareToken_(outcome);
        const shareToken = new ShareToken(this.connector, this.accountManager, shareTokenAddress, TestFixture.GAS_PRICE);
        return await shareToken.balanceOf_(this.accountManager.defaultAddress);
    }

    public async getFeeWindow(market: Market): Promise<FeeWindow> {
        const feeWindowAddress = await market.getFeeWindow_();
        await this.linkDebugSymbolsForContract('FeeWindow', feeWindowAddress);
        return new FeeWindow(this.connector, this.accountManager, feeWindowAddress, TestFixture.GAS_PRICE);
    }

    public async getReportingParticipant(reportingParticipantAddress: string): Promise<DisputeCrowdsourcer> {
        return new DisputeCrowdsourcer(this.connector, this.accountManager, reportingParticipantAddress, TestFixture.GAS_PRICE);
    }

    public async getUniverse(market: Market): Promise<Universe> {
        const universeAddress = await market.getUniverse_();
        return new Universe(this.connector, this.accountManager, universeAddress, TestFixture.GAS_PRICE);
    }

    public async getWinningReportingParticipant(market: Market): Promise<DisputeCrowdsourcer> {
        const reportingParticipantAddress = await market.getWinningReportingParticipant_();
        return new DisputeCrowdsourcer(this.connector, this.accountManager, reportingParticipantAddress, TestFixture.GAS_PRICE);
    }

    public async setTimestamp(timestamp: BN): Promise<void> {
        const timeContract = await this.contractDeployer.getContract("TimeControlled");
        const time = new TimeControlled(this.connector, this.accountManager, timeContract.address, TestFixture.GAS_PRICE);
        await time.setTimestamp(timestamp);
        return;
    }

    public async getTimestamp(): Promise<BN> {
        return this.contractDeployer.controller.getTimestamp_();
    }

    public async doInitialReport(market: Market, payoutNumerators: Array<BN>, invalid: boolean): Promise<void> {
        await market.doInitialReport(payoutNumerators, invalid, "");
        return;
    }

    public async finalizeMarket(market: Market): Promise<void> {
        await market.finalize();
        return;
    }

    public async getLegacyRepBalance(owner: string): Promise<BN> {
        const legacyRepContract = await this.contractDeployer.getContract("LegacyReputationToken");
        const legacyRep = new LegacyReputationToken(this.connector, this.accountManager, legacyRepContract.address, TestFixture.GAS_PRICE);
        return await legacyRep.balanceOf_(owner);
    }

    public async getLegacyRepAllowance(owner: string, spender: string): Promise<BN> {
        const legacyRepContract = await this.contractDeployer.getContract("LegacyReputationToken");
        const legacyRep = new LegacyReputationToken(this.connector, this.accountManager, legacyRepContract.address, TestFixture.GAS_PRICE);
        return await legacyRep.allowance_(owner, spender);
    }

    public async transferLegacyRep(to: string, amount: BN): Promise<void> {
        const legacyRepContract = await this.contractDeployer.getContract("LegacyReputationToken");
        const legacyRep = new LegacyReputationToken(this.connector, this.accountManager, legacyRepContract.address, TestFixture.GAS_PRICE);
        await legacyRep.transfer(to, amount);
        return;
    }

    public async approveLegacyRep(spender: string, amount: BN): Promise<void> {
        const legacyRepContract = await this.contractDeployer.getContract("LegacyReputationToken");
        const legacyRep = new LegacyReputationToken(this.connector, this.accountManager, legacyRepContract.address, TestFixture.GAS_PRICE);
        await legacyRep.approve(spender, amount);
        return;
    }

    public async getChildUniverseReputationToken(parentPayoutDistributionHash: string) {
        const childUniverseAddress = await this.contractDeployer.universe.getChildUniverse_(parentPayoutDistributionHash);
        const childUniverse = new Universe(this.connector, this.accountManager, childUniverseAddress, TestFixture.GAS_PRICE);
        const repContractAddress = await childUniverse.getReputationToken_();
        return new ReputationToken(this.connector, this.accountManager, repContractAddress, TestFixture.GAS_PRICE);
    }

    public async getReputationToken(): Promise<ReputationToken> {
        const repContractAddress = await this.contractDeployer.universe.getReputationToken_();
        return new ReputationToken(this.connector, this.accountManager, repContractAddress, TestFixture.GAS_PRICE);
    }

    // TODO: Determine why ETH balance doesn't change when buying complete sets or redeeming reporting participants
    public async getEthBalance(): Promise<BN> {
        return await this.connector.ethjsQuery.getBalance(this.accountManager.defaultAddress);
    }

    public async getRepBalance(owner: string): Promise<BN> {
        const rep = await this.getReputationToken();
        return await rep.balanceOf_(owner);
    }

    public async getRepAllowance(owner: string, spender: string): Promise<BN> {
        const rep = await this.getReputationToken();
        return await rep.allowance_(owner, spender);
    }
}
