import BN = require('bn.js');
import { TestRpc } from './TestRpc';
import { Configuration } from '../libraries/Configuration';
import { Connector } from '../libraries/Connector';
import { AccountManager } from '../libraries/AccountManager';
import { ContractCompiler } from '../libraries/ContractCompiler';
import { ContractDeployer } from '../libraries/ContractDeployer';
import { FeeWindow, ShareToken, CompleteSets, TimeControlled, LegacyReputationToken, Cash, Universe, ReputationToken, Market, CreateOrder, Orders, Trade, CancelOrder } from '../libraries/ContractInterfaces';
import { stringTo32ByteHex } from '../libraries/HelperFunctions';

export class TestFixture {
    private readonly configuration: Configuration;
    private readonly connector: Connector;
    private readonly accountManager: AccountManager;
    // FIXME: extract out the bits of contract deployer that we need access to, like the contracts/abis, so we can have a more targeted dependency
    private readonly contractDeployer: ContractDeployer;

    public get universe() { return this.contractDeployer.universe; }
    public get cash() { return <Cash> this.contractDeployer.getContract('Cash'); }

    public constructor(configuration: Configuration, connector: Connector, accountManager: AccountManager, contractDeployer: ContractDeployer) {
        this.configuration = configuration;
        this.connector = connector;
        this.accountManager = accountManager;
        this.contractDeployer = contractDeployer;
    }

    public static create = async (): Promise<TestFixture> => {
        const configuration = await Configuration.create(false, false);
        await TestRpc.startTestRpcIfNecessary(configuration);
        const compiledContracts = await new ContractCompiler(configuration).compileContracts();
        const connector = new Connector(configuration);
        const accountManager = new AccountManager(configuration, connector);
        const contractDeployer = new ContractDeployer(configuration, connector, accountManager, compiledContracts);
        await contractDeployer.deploy();
        return new TestFixture(configuration, connector, accountManager, contractDeployer);
    }

    public async approveCentralAuthority(): Promise<void> {
        const authority = this.contractDeployer.getContract('Augur');
        const cash = new Cash(this.connector, this.accountManager, this.contractDeployer.getContract('Cash').address, this.configuration.gasPrice);
        await cash.approve(authority.address, new BN(2).pow(new BN(256)).sub(new BN(1)));
    }

    public async createMarket(universe: Universe, outcomes: string[], endTime: BN, feePerEthInWei: BN, denominationToken: string, designatedReporter: string): Promise<Market> {
        const legacyReputationToken = new LegacyReputationToken(this.connector, this.accountManager, this.contractDeployer.getContract('LegacyReputationToken').address, this.configuration.gasPrice);
        const reputationTokenAddress = await universe.getReputationToken_();
        const reputationToken = new ReputationToken(this.connector, this.accountManager, reputationTokenAddress, this.configuration.gasPrice);

        // get some REP
        // TODO: just get enough REP to cover the bonds rather than over-allocating
        await legacyReputationToken.faucet(new BN(0));
        await legacyReputationToken.approve(reputationTokenAddress, new BN(2).pow(new BN(256)).sub(new BN(1)));
        await reputationToken.migrateFromLegacyReputationToken();

        const marketCreationFee = await universe.getOrCacheMarketCreationCost_();

        const marketAddress = await universe.createCategoricalMarket_(endTime, feePerEthInWei, denominationToken, designatedReporter, outcomes, stringTo32ByteHex(" "), 'description', '', { attachedEth: marketCreationFee });
        if (!marketAddress || marketAddress == "0x") {
            throw new Error("Unable to get address for new categorical market.");
        }
        await universe.createCategoricalMarket(endTime, feePerEthInWei, denominationToken, designatedReporter, outcomes, stringTo32ByteHex(" "), 'description', '', { attachedEth: marketCreationFee });
        const market = new Market(this.connector, this.accountManager, marketAddress, this.configuration.gasPrice);
        if (await market.getTypeName_() !== stringTo32ByteHex("Market")) {
            throw new Error("Unable to create new categorical market");
        }
        return market;
    }

    public async createReasonableMarket(universe: Universe, denominationToken: string, outcomes: string[]): Promise<Market> {
        const endTime = new BN(Math.round(new Date().getTime() / 1000) + 30 * 24 * 60 * 60);
        const fee = (new BN(10)).pow(new BN(16));
        return await this.createMarket(universe, outcomes, endTime, fee, denominationToken, this.accountManager.defaultAddress);
    }

    public async placeOrder(market: string, type: BN, numShares: BN, price: BN, outcome: BN, betterOrderID: string, worseOrderID: string, tradeGroupID: string): Promise<void> {
        const createOrderContract = await this.contractDeployer.getContract("CreateOrder");
        const createOrder = new CreateOrder(this.connector, this.accountManager, createOrderContract.address, this.configuration.gasPrice);

        const ethValue = numShares.mul(price);

        await createOrder.publicCreateOrder(type, numShares, price, market, outcome, betterOrderID, worseOrderID, tradeGroupID, { attachedEth: ethValue });
        return;
    }

    public async takeBestOrder(marketAddress: string, type: BN, numShares: BN, price: BN, outcome: BN, tradeGroupID: string): Promise<void> {
        const tradeContract = await this.contractDeployer.getContract("Trade");
        const trade = new Trade(this.connector, this.accountManager, tradeContract.address, this.configuration.gasPrice);

        let actualPrice = price;
        if (type == new BN(1)) {
            const market = new Market(this.connector, this.accountManager, marketAddress, this.configuration.gasPrice);
            const numTicks = await market.getNumTicks_();
            actualPrice = numTicks.sub(price);
        }
        const ethValue = numShares.mul(actualPrice);

        const bestPriceAmount = await trade.publicTakeBestOrder_(type, marketAddress, outcome, numShares, price, tradeGroupID, { attachedEth: ethValue });
        if (bestPriceAmount == new BN(0)) {
            throw new Error("Could not take best Order");
        }

        await trade.publicTakeBestOrder(type, marketAddress, outcome, numShares, price, tradeGroupID, { attachedEth: ethValue });
        return;
    }

    public async cancelOrder(orderID: string): Promise<void> {
        const cancelOrderContract = await this.contractDeployer.getContract("CancelOrder");
        const cancelOrder = new CancelOrder(this.connector, this.accountManager, cancelOrderContract.address, this.configuration.gasPrice);

        await cancelOrder.cancelOrder(orderID);
        return;
    }

    public async getOrderPrice(orderID: string): Promise<BN> {
        const ordersContract = await this.contractDeployer.getContract("Orders");
        const orders = new Orders(this.connector, this.accountManager, ordersContract.address, this.configuration.gasPrice);

        const price = await orders.getPrice_(orderID);
        if (price.toNumber() == 0) {
            throw new Error("Unable to get order price");
        }
        return price;
    }

    public async getOrderAmount(orderID: string): Promise<BN> {
        const ordersContract = await this.contractDeployer.getContract("Orders");
        const orders = new Orders(this.connector, this.accountManager, ordersContract.address, this.configuration.gasPrice);
        return await orders.getAmount_(orderID);
    }

    public async getBestOrderId(type: BN, market: string, outcome: BN): Promise<string> {
        const ordersContract = await this.contractDeployer.getContract("Orders");
        const orders = new Orders(this.connector, this.accountManager, ordersContract.address, this.configuration.gasPrice);

        const orderID = await orders.getBestOrderId_(type, market, outcome);
        if (!orderID) {
            throw new Error("Unable to get order price");
        }
        return orderID;
    }

    public async buyCompleteSets(market: Market, amount: BN): Promise<void> {
        const completeSetsContract = await this.contractDeployer.getContract("CompleteSets");
        const completeSets = new CompleteSets(this.connector, this.accountManager, completeSetsContract.address, this.configuration.gasPrice);

        const numTicks = await market.getNumTicks_();
        const ethValue = amount.mul(numTicks);

        await completeSets.publicBuyCompleteSets(market.address, amount, { attachedEth: ethValue });
        return;
    }

    public async contribute(market: Market, payoutNumerators: Array<BN>, invalid: boolean, amount: BN): Promise<void> {                
        await market.contribute(payoutNumerators, invalid, amount);
        return;
    }

    public async getNumSharesInMarket(market: Market, outcome: BN): Promise<BN> {
        const shareTokenAddress = await market.getShareToken_(outcome);
        const shareToken = new ShareToken(this.connector, this.accountManager, shareTokenAddress, this.configuration.gasPrice);
        return await shareToken.balanceOf_(this.accountManager.defaultAddress);
    }

    public async getFeeWindow(market: Market): Promise<FeeWindow> {
        const feeWindowAddress = await market.getFeeWindow_();
        return new FeeWindow(this.connector, this.accountManager, feeWindowAddress, this.configuration.gasPrice);
    }

    public async setTimestamp(timestamp: BN): Promise<void> {
        const timeContract = await this.contractDeployer.getContract("TimeControlled");
        const time = new TimeControlled(this.connector, this.accountManager, timeContract.address, this.configuration.gasPrice);
        await time.setTimestamp(timestamp);
        return;
    }

    public async getTimestamp(): Promise<BN> {
        return this.contractDeployer.controller.getTimestamp_();
    }

    public async doInitialReport(market: Market, payoutNumerators: Array<BN>, invalid: boolean): Promise<void> {
        await market.doInitialReport(payoutNumerators, invalid);
        return;
    }

    public async finalizeMarket(market: Market): Promise<void> {
        await market.finalize();
        return;
    }
}
