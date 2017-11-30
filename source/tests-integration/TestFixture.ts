import BN = require('bn.js');
import { TestRpc } from './TestRpc';
import { Configuration } from '../libraries/Configuration';
import { Connector } from '../libraries/Connector';
import { AccountManager } from '../libraries/AccountManager';
import { ContractCompiler } from '../libraries/ContractCompiler';
import { ContractDeployer } from '../libraries/ContractDeployer';
import { LegacyReputationToken, Cash, Universe, ReputationToken, Market, CreateOrder, Orders } from '../libraries/ContractInterfaces';
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
        this.contractDeployer = contractDeployer
    }

    public static create = async (): Promise<TestFixture> => {
        const configuration = await Configuration.create();
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
        const transactionHash = await cash.approve(authority.address, new BN(2).pow(new BN(256)).sub(new BN(1)));
        await this.connector.waitForTransactionReceipt(transactionHash, `Approving central authority.`);
    }

    public async createMarket(universe: Universe, numOutcomes: BN, endTime: BN, feePerEthInWei: BN, denominationToken: string, designatedReporter: string): Promise<Market> {
        const legacyReputationToken = new LegacyReputationToken(this.connector, this.accountManager, this.contractDeployer.getContract('LegacyReputationToken').address, this.configuration.gasPrice);
        const reputationTokenAddress = await universe.getReputationToken_();
        const reputationToken = new ReputationToken(this.connector, this.accountManager, reputationTokenAddress, this.configuration.gasPrice);

        // get some REP
        // TODO: just get enough REP to cover the bonds rather than over-allocating
        const repFaucetTransactionHash = await legacyReputationToken.faucet(new BN(0));
        const repApprovalTransactionHash = await legacyReputationToken.approve(reputationTokenAddress, new BN(2).pow(new BN(256)).sub(new BN(1)));
        await this.connector.waitForTransactionReceipt(repFaucetTransactionHash, `Using legacy reputation faucet.`);
        await this.connector.waitForTransactionReceipt(repApprovalTransactionHash, `Approving legacy reputation.`);
        const repMigrationTransactionHash = await reputationToken.migrateFromLegacyReputationToken();
        await this.connector.waitForTransactionReceipt(repMigrationTransactionHash, `Migrating reputation.`);

        const marketCreationFee = await universe.getOrCacheMarketCreationCost_();
        const marketAddress = await universe.createCategoricalMarket_(endTime, feePerEthInWei, denominationToken, designatedReporter, numOutcomes, stringTo32ByteHex(" "), stringTo32ByteHex("description"), '', { attachedEth: marketCreationFee });
        if (!marketAddress) {
            throw new Error("Unable to get address for new categorical market.");
        }
        const createMarketTransactionHash = await universe.createCategoricalMarket(endTime, feePerEthInWei, denominationToken, designatedReporter, numOutcomes, stringTo32ByteHex(" "), stringTo32ByteHex("description"), '', { attachedEth: marketCreationFee });
        await this.connector.waitForTransactionReceipt(createMarketTransactionHash, `Creating market.`);
        const market = new Market(this.connector, this.accountManager, marketAddress, this.configuration.gasPrice);

        if (await market.getTypeName_() !== stringTo32ByteHex("Market")) {
            throw new Error("Unable to create new categorical market");
        }
        return market;
    }

    public async createReasonableMarket(universe: Universe, denominationToken: string, numOutcomes: BN): Promise<Market> {
        const endTime = new BN(Math.round(new Date().getTime() / 1000));
        const fee = (new BN(10)).pow(new BN(16));
        return await this.createMarket(universe, numOutcomes, endTime, fee, denominationToken, this.accountManager.defaultAddress);
    }

    public async placeOrder(market: string, type: BN, numShares: BN, price: BN, outcome: BN, betterOrderID: string, worseOrderID: string, tradeGroupID: string): Promise<void> {
        const createOrderContract = await this.contractDeployer.getContract("CreateOrder");
        const createOrder = new CreateOrder(this.connector, this.accountManager, createOrderContract.address, this.configuration.gasPrice);

        const ethValue = numShares.mul(price);

        const placeOrderTransactionHash = await createOrder.publicCreateOrder(type, numShares, price, market, outcome, betterOrderID, worseOrderID, tradeGroupID, { attachedEth: ethValue });
        const receipt = await this.connector.waitForTransactionReceipt(placeOrderTransactionHash, `Placing Order.`);
        if (receipt.status != 1) {
            throw new Error("Could not create Order");
        }
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

    public async getBestOrderId(type: BN, market: string, outcome: BN): Promise<string> {
        const ordersContract = await this.contractDeployer.getContract("Orders");
        const orders = new Orders(this.connector, this.accountManager, ordersContract.address, this.configuration.gasPrice);

        const orderID = await orders.getBestOrderId_(type, market, outcome);
        if (!orderID) {
            throw new Error("Unable to get order price");
        }
        return orderID;
    }
}
