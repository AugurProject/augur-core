import BN = require('bn.js');
import { TestRpc } from './TestRpc';
import { Configuration } from '../libraries/Configuration';
import { Connector } from '../libraries/Connector';
import { AccountManager } from '../libraries/AccountManager';
import { ContractCompiler } from '../libraries/ContractCompiler';
import { ContractDeployer } from '../libraries/ContractDeployer';
import { LegacyReputationToken, Cash, Universe, ReputationToken, ReportingWindow, Market } from '../libraries/ContractInterfaces';
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

    public async createMarket(universe: Universe, numOutcomes: number, endTime: number, feePerEthInWei: number, denominationToken: string, designatedReporter: string, numTicks: number): Promise<Market> {
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
        // necessary because it is used part of market creation fee calculation
        const currentReportingWindowTransactionHash = await universe.getOrCreateCurrentReportingWindow();
        // necessary because it is used as part of market creation fee calculation
        const previousReportingWindowTransactionHash = await universe.getOrCreatePreviousReportingWindow();
        // necessary because createMarket needs its reporting window already created
        const marketReportingWindowTransactionHash = await universe.getOrCreateReportingWindowByMarketEndTime(endTime);
        await this.connector.waitForTransactionReceipt(repMigrationTransactionHash, `Migrating reputation.`);
        await this.connector.waitForTransactionReceipt(currentReportingWindowTransactionHash, `Instantiating current reporting window.`);
        await this.connector.waitForTransactionReceipt(previousReportingWindowTransactionHash, `Instantiating previous reporting window.`);
        await this.connector.waitForTransactionReceipt(marketReportingWindowTransactionHash, `Instantiating market reporting window.`);

        const targetReportingWindowAddress = await universe.getOrCreateReportingWindowByMarketEndTime_(endTime);

        const targetReportingWindow = new ReportingWindow(this.connector, this.accountManager, targetReportingWindowAddress, this.configuration.gasPrice);
        const marketCreationFee = await universe.getMarketCreationCost_();
        const marketAddress = await targetReportingWindow.createMarket_(endTime, numOutcomes, numTicks, feePerEthInWei, denominationToken, designatedReporter, '', { attachedEth: marketCreationFee });
        if (!marketAddress) {
            throw new Error("Unable to get address for new categorical market.");
        }
        const createMarketTransactionHash = await targetReportingWindow.createMarket(endTime, numOutcomes, numTicks, feePerEthInWei, denominationToken, designatedReporter, '', { attachedEth: marketCreationFee });
        await this.connector.waitForTransactionReceipt(createMarketTransactionHash, `Creating market.`);
        const market = new Market(this.connector, this.accountManager, marketAddress, this.configuration.gasPrice);

        if (await market.getTypeName_() !== stringTo32ByteHex("Market")) {
            throw new Error("Unable to create new categorical market");
        }
        return market;
    }

    public async createReasonableMarket(universe: Universe, denominationToken: string, numOutcomes: number): Promise<Market> {
        const endTime = Math.round(new Date().getTime() / 1000);
        return await this.createMarket(universe, numOutcomes, endTime, 10 ** 16, denominationToken, this.accountManager.defaultAddress, 10 ** 4);
    }
}
