import { Connector } from '../libraries/Connector';
import { AccountManager } from '../libraries/AccountManager';
import { NetworkConfiguration } from '../libraries/NetworkConfiguration';
import { LegacyReputationToken, ReputationToken } from '../libraries/ContractInterfaces';
import { resolveAll } from "../libraries/HelperFunctions";

export interface LegacyRepData {
    balances: Array<string>;
    allowanceOwners: Array<string>;
    allowanceSpenders: Array<string>;
}

export class LegacyRepMigrator {
    private readonly repContract: ReputationToken;
    private readonly legacyRepContract: LegacyReputationToken;
    private legacyRepData: LegacyRepData;
    private unmigratedLegacyRepData: LegacyRepData;
    private chunkedBalances: Array<Array<string>>;
    private chunkedAllowanceOwners: Array<Array<string>>;
    private chunkedAllowanceSpenders: Array<Array<string>>;
    private readonly chunkSize: number;

    private constructor(repContract: ReputationToken, legacyRepContract: LegacyReputationToken, legacyRepData: LegacyRepData, chunkSize: number) {
        this.repContract = repContract;
        this.legacyRepContract = legacyRepContract;
        this.chunkSize = chunkSize;
        this.legacyRepData = legacyRepData;
        this.unmigratedLegacyRepData = {
            balances: [],
            allowanceOwners: [],
            allowanceSpenders: []
        };
        this.chunkedBalances = [];
        this.chunkedAllowanceOwners = [];
        this.chunkedAllowanceSpenders = [];
    }

    private async initialize(): Promise<void> {
        await this.getUnMigratedLegacyData(this.legacyRepData);
        this.chunkedBalances = this.chunk(this.unmigratedLegacyRepData.balances);
        this.chunkedAllowanceOwners = this.chunk(this.unmigratedLegacyRepData.allowanceOwners);
        this.chunkedAllowanceSpenders = this.chunk(this.unmigratedLegacyRepData.allowanceSpenders);
    }

    public static create = async (legacyRepData: LegacyRepData, repContractAddress: string, txSize: number): Promise<LegacyRepMigrator> => {
        const networkConfiguration = NetworkConfiguration.create();
        const connector = new Connector(networkConfiguration);
        console.log(`Waiting for connection to: ${networkConfiguration.networkName} at ${networkConfiguration.http}`);
        await connector.waitUntilConnected();
        const accountManager = new AccountManager(connector, networkConfiguration.privateKey);

        console.log(`Using REP Contract at: ${repContractAddress}`);
        const repContract = new ReputationToken(connector, accountManager, repContractAddress, connector.gasPrice);

        const legacyRepContractAddress = await repContract.getLegacyRepToken_();
        const legacyRepContract = new LegacyReputationToken(connector, accountManager, legacyRepContractAddress, connector.gasPrice);

        const isPaused = await legacyRepContract.paused_();
        if (!isPaused) {
            throw new Error("Legacy REP contract must be paused! You should pause it an re-collect balances and allowances");
        }

        const legacyRepMigrator = new LegacyRepMigrator(repContract, legacyRepContract, legacyRepData, txSize);
        await legacyRepMigrator.initialize();

        return legacyRepMigrator;
    }

    public async migrateLegacyRep(): Promise<void> {

        console.log("Migrating Approvals");
        await this.migrateApprovals();
        console.log("Verifying Approvals");
        await this.verifyApprovals();
        console.log("Migrating Approvals Complete");

        console.log("Migrating Balances");
        await this.migrateBalances();
        console.log("Verifying Balances");
        await this.verifyBalances();
        console.log("Migrating Balances Complete");

        return;
    }

    private async migrateApprovals(): Promise<void> {
        const promises: Array<Promise<any>> = [];
        for (let i = 0; i < this.chunkedAllowanceOwners.length; i++) {
            promises.push(this.migrateAllowances(this.chunkedAllowanceOwners[i], this.chunkedAllowanceSpenders[i]));
        }
        await resolveAll(promises);
        return;
    }

    private async migrateAllowances(owners: Array<string>, spenders: Array<string>): Promise<void> {
        await this.repContract.migrateAllowancesFromLegacyRep(owners, spenders);
        return;
    }

    private async migrateBalances(): Promise<void> {
        const promises: Array<Promise<any>> = [];
        for (let balancesChunk of this.chunkedBalances) {
            promises.push(this.migrateOwners(balancesChunk));
        }
        await resolveAll(promises);
        return;
    }

    private async migrateOwners(owners: Array<string>): Promise<void> {
        await this.repContract.migrateBalancesFromLegacyRep(owners);
        const supply = await this.repContract.totalSupply_();
        console.log(`Total Rep Supply: ${supply}`);
        return;
    }

    private async verifyApprovals(): Promise<void> {
        const promises: Array<Promise<any>> = [];

        for (let i = 0; i < this.legacyRepData.allowanceOwners.length; i++) {
            promises.push(this.verifyApproval(
                this.legacyRepData.allowanceOwners[i],
                this.legacyRepData.allowanceSpenders[i],
            ));
        }

        await resolveAll(promises);
        return;
    }

    private async verifyApproval(owner: string, spender: string): Promise<void> {
        const legacyAllowance = await this.legacyRepContract.allowance_(owner, spender);
        const allowance = await this.repContract.allowance_(owner, spender);
        if (!allowance.eq(legacyAllowance)) {
            throw new Error(`Allowance mismatch: OWNER: ${owner} SPENDER: ${spender} LEGACY: ${legacyAllowance} CURRENT: ${allowance}`);
        }
        return;
    }

    private async verifyBalances(): Promise<void> {
        const promises: Array<Promise<any>> = [];

        for (let owner of this.legacyRepData.balances) {
            promises.push(this.verifyBalance(owner));
        }

        await resolveAll(promises);
        return;
    }

    private async verifyBalance(owner: string): Promise<void> {
        const legacyBalance = await this.legacyRepContract.balanceOf_(owner);
        const balance = await this.repContract.balanceOf_(owner);
        if (!balance.eq(legacyBalance)) {
            throw new Error(`Allowance mismatch: OWNER: ${owner} LEGACY: ${legacyBalance} CURRENT: ${balance}`);
        }
        return;
    }

    private chunk(items: Array<string>): Array<Array<string>> {
        const numChunks = Math.ceil(items.length / this.chunkSize);
        const chunked = new Array(numChunks);
        for (let i = 1; i <= numChunks; ++i) {
            chunked[i - 1] = items.slice((i - 1) * this.chunkSize, i * this.chunkSize);
        }
        return chunked;
    }

    private async getUnMigratedLegacyData(legacyRepData: LegacyRepData): Promise<void> {
        const promises: Array<Promise<any>> = [];

        for (let i = 0; i < legacyRepData.allowanceOwners.length; i++) {
            promises.push(this.addToAllowancesIfUnmigrated(
                legacyRepData.allowanceOwners[i],
                legacyRepData.allowanceSpenders[i],
            ));
        }

        for (let owner of legacyRepData.balances) {
            promises.push(this.addToBalancesIfUnmigrated(owner));
        }

        await resolveAll(promises);
        return;
    }

    private async addToBalancesIfUnmigrated(address: string): Promise<void> {
        const balance = await this.repContract.balanceOf_(address);
        if (balance.isZero()) {
            this.unmigratedLegacyRepData.balances.push(address);
        }
        return;
    }

    private async addToAllowancesIfUnmigrated(owner: string, spender: string): Promise<void> {
        const allowance = await this.repContract.allowance_(owner, spender);
        if (allowance.isZero()) {
            this.unmigratedLegacyRepData.allowanceOwners.push(owner);
            this.unmigratedLegacyRepData.allowanceSpenders.push(spender);
        }
        return;
    }
}
